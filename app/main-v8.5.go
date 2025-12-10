package main

import (
	"encoding/binary"
	"fmt"
	"log"
	"math"
	"net"
	"os"
	"strconv"
	"sync"
	"time"
)

// --- 1. 參數設定 ---
const (
	ModbusTimeout    = 3 * time.Second
	PollingInterval  = 2 * time.Second
	SuccessWaitTime  = 500 * time.Millisecond
	TestRuns         = 60
	B1ResponseLength = 93
	VoltageScale     = 100.0
)

var (
	ModbusHost = os.Getenv("MODBUS_HOST")
	ModbusPort = os.Getenv("MODBUS_PORT")
	SlaveID    = 1
	
	SuccessCount int
	TotalTime    time.Duration
	StatsMutex   sync.Mutex
	wg           sync.WaitGroup
)

func init() {
	log.SetOutput(os.Stdout)
	log.SetFlags(log.Ldate | log.Ltime | log.Lmicroseconds)
	if os.Getenv("SLAVE_ID") != "" {
		if id, err := strconv.Atoi(os.Getenv("SLAVE_ID")); err == nil {
			SlaveID = id
		}
	}
	if ModbusHost == "" { ModbusHost = "192.168.106.12" }
	if ModbusPort == "" { ModbusPort = "502" }
}

// --- 2. RobustTCPClient (Python 1:1 移植) ---

type RobustTCPClient struct {
	Host    string
	Port    string
	Timeout time.Duration
	Conn    net.Conn
}

func NewClient(host, port string, timeout time.Duration) *RobustTCPClient {
	return &RobustTCPClient{Host: host, Port: port, Timeout: timeout}
}

// 對應 Python: connect(self)
func (c *RobustTCPClient) connect() error {
	c.close() // Python: self.close() # 先確保舊的已關閉

	addr := c.Host + ":" + c.Port
	// Python: socket.socket(AF_INET, SOCK_STREAM) + connect
	conn, err := net.DialTimeout("tcp", addr, c.Timeout)
	if err != nil {
		return err
	}

	// Python: setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	if tcpConn, ok := conn.(*net.TCPConn); ok {
		tcpConn.SetNoDelay(true)
	}

	// Python: time.sleep(0.1)
	time.Sleep(100 * time.Millisecond)

	c.Conn = conn
	return nil
}

// 對應 Python: close(self)
func (c *RobustTCPClient) close() {
	if c.Conn != nil {
		c.Conn.Close()
	}
	c.Conn = nil
}

// 對應 Python: flush_buffer(self)
func (c *RobustTCPClient) flush_buffer() {
	if c.Conn == nil {
		return
	}
	
	// Python: self._sock.settimeout(0.05)
	c.Conn.SetReadDeadline(time.Now().Add(50 * time.Millisecond))
	
	tmpBuf := make([]byte, 4096)
	for {
		// Python: chunk = self._sock.recv(4096)
		n, err := c.Conn.Read(tmpBuf)
		if err != nil {
			// Python: except socket.timeout: pass
			// Go: 如果是 Timeout，代表清空完畢，正常退出
			if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
				break 
			}
			// Python: except Exception: self.close()
			// 其他錯誤則關閉連線
			c.close()
			break
		}
		if n == 0 { break }
		// log.Printf("🔥 捨棄殘留數據: %d bytes", n)
	}
}

// 對應 Python: send(self, data)
func (c *RobustTCPClient) send(data []byte) error {
	if c.Conn == nil {
		if err := c.connect(); err != nil {
			return err
		}
	}

	// Python: self.flush_buffer() # 🔥 發送前先清場
	c.flush_buffer()

	// Python: self._sock.settimeout(self.timeout)
	c.Conn.SetWriteDeadline(time.Now().Add(c.Timeout))

	// Python: self._sock.sendall(data)
	_, err := c.Conn.Write(data)
	if err != nil {
		c.close()
		return err
	}
	return nil
}

// 對應 Python: recv_fixed(self, length)
func (c *RobustTCPClient) recv_fixed(length int) ([]byte, error) {
	if c.Conn == nil { return nil, fmt.Errorf("no connection") }

	data := make([]byte, 0, length)
	startTime := time.Now()

	// Python: self._sock.settimeout(self.timeout)
	// Go 需要在 Read 前設置 Deadline
	c.Conn.SetReadDeadline(time.Now().Add(c.Timeout))

	tmpBuf := make([]byte, length) // 暫存區

	// Python: while len(data) < length:
	for len(data) < length {
		// Python: if (time.time() - start_time) > self.timeout:
		if time.Since(startTime) > c.Timeout {
			if len(data) > 0 {
				log.Printf("⚠️ 接收超時，僅收到 %d/%d bytes", len(data), length)
			}
			return nil, fmt.Errorf("timeout")
		}

		needed := length - len(data)
		// Python: chunk = self._sock.recv(needed)
		n, err := c.Conn.Read(tmpBuf[:needed])
		
		if err != nil {
			c.close()
			return nil, err
		}
		if n == 0 {
			c.close()
			return nil, fmt.Errorf("connection closed by peer")
		}

		data = append(data, tmpBuf[:n]...)
	}

	return data, nil
}

// --- 3. 業務邏輯 (保持不變) ---

func calcChecksum(data []byte) byte {
	var sum byte = 0
	for _, b := range data { sum += b }
	return sum
}

func decodeData(raw []byte) (float64, float64) {
	vRaw := binary.BigEndian.Uint16(raw[32:34])
	volt := float64(vRaw) / 100.0
	yRaw := binary.BigEndian.Uint32(raw[44:48])
	yield := float64(yRaw)
	volt = math.Round(volt*100) / 100
	return volt, yield
}

// --- 4. 測試執行 ---

func runSingleTest(index int) {
	defer wg.Done()
	
	// 注意：為了完全模擬 Python，這裡使用長效連線模式，
	// 但 RobustTCPClient 內部的 send() 會自動處理 connect()
	// 所以我們這裡每次 NewClient 也沒關係，重點是 RobustTCPClient 內部的行為
	client := NewClient(ModbusHost, ModbusPort, ModbusTimeout)
	
	req := []byte{byte(SlaveID), 0xB1, 0x01, 0x00, 0x00, 0x00, 0x00}
	req = append(req, calcChecksum(req))

	start := time.Now()
	
	// 執行 Python 邏輯: send -> recv
	var err error
	var resp []byte

	if err = client.send(req); err == nil {
		resp, err = client.recv_fixed(B1ResponseLength)
	}

	duration := time.Since(start)
	
	// 測試結束後關閉 (模擬 Python 腳本結束或下一次迴圈)
	// 在 Python 長效模式下通常不關，但在單次測試中我們主動關閉以釋放資源
	client.close()

	StatsMutex.Lock()
	defer StatsMutex.Unlock()

	if err == nil && resp != nil {
		SuccessCount++
		TotalTime += duration
		volt, yield := decodeData(resp)
		log.Printf("[TEST %02d] ✅ 成功: %.3fs | 電壓: %.2f V | 發電量: %.0f Wh", index, duration.Seconds(), volt, yield)
		time.Sleep(SuccessWaitTime)
	} else {
		log.Printf("[TEST %02d] ❌ 失敗: %.3fs | 錯誤: %v", index, duration.Seconds(), err)
	}
}

func main() {
	log.Println("=======================================")
	log.Printf("Go 語言 V8.5 (Python 1:1 移植版)")
	log.Printf("特色: Flush Buffer + NoDelay + Strict Timing")
	log.Printf("目標: %s:%s (UID: %d)", ModbusHost, ModbusPort, SlaveID)
	log.Println("=======================================")

	overallStart := time.Now()

	for i := 1; i <= TestRuns; i++ {
		wg.Add(1)
		// 使用 Goroutine 執行，避免阻塞主線程計時
		go runSingleTest(i)
		time.Sleep(PollingInterval)
	}

	wg.Wait()
	
	overallDuration := time.Since(overallStart)
	
	log.Println("\n================= 最終評估報告 =================")
	log.Printf("總運行時間: %.2f 秒", overallDuration.Seconds())
	log.Printf("成功率    : %.1f%% (%d/%d)", float64(SuccessCount)/float64(TestRuns)*100, SuccessCount, TestRuns)
	
	if SuccessCount > 0 {
		avgSeconds := TotalTime.Seconds() / float64(SuccessCount)
		log.Printf("平均回應  : %.3f 秒", avgSeconds)
	}
	log.Println("================================================")
}
