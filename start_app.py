import os
import subprocess
import sys
import time
import webbrowser
import psutil
import socket
from threading import Thread

BACKEND_PORT = 5000
FRONTEND_PORT = 8080

backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(backend_dir, 'static')

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

def kill_process_on_port(port):
    """杀死占用指定端口的进程"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections']:
                    if conn.laddr.port == port:
                        print(f"正在终止占用端口 {port} 的进程: {proc.info['name']} (PID: {proc.info['pid']})")
                        psutil.Process(proc.info['pid']).terminate()
                        time.sleep(1)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"清理端口 {port} 时出错: {e}")
    return False

def run_backend():
    """启动 Flask 后端"""
    try:
        # 检查并清理端口
        if is_port_in_use(BACKEND_PORT):
            print(f"端口 {BACKEND_PORT} 被占用，正在清理...")
            kill_process_on_port(BACKEND_PORT)
            time.sleep(2)
        
        # 设置环境变量
        env = os.environ.copy()
        env_file = os.path.join(backend_dir, '.env')
        if os.path.exists(env_file):
            print("正在加载 .env 文件...")
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env[key] = value.strip('"').strip("'")
        
        print(f"正在启动 Flask 后端 (端口 {BACKEND_PORT})...")
        # 使用 subprocess.Popen 启动后端，并设置工作目录
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待后端启动
        print("等待后端服务启动...")
        time.sleep(8)  # 给Flask足够的启动时间
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print(f"✅ Flask 后端已成功启动在端口 {BACKEND_PORT}")
            return process
        else:
            print(f"❌ Flask 后端启动失败")
            return None
            
    except Exception as e:
        print(f"❌ 启动后端时出错: {e}")
        return None

def run_frontend_server():
    """启动前端静态服务器"""
    try:
        # 检查并清理端口
        if is_port_in_use(FRONTEND_PORT):
            print(f"端口 {FRONTEND_PORT} 被占用，正在清理...")
            kill_process_on_port(FRONTEND_PORT)
            time.sleep(2)
        
        print(f"正在启动前端服务器 (端口 {FRONTEND_PORT})...")
        
        # 确保前端目录存在
        if not os.path.exists(frontend_dir):
            print(f"❌ 前端目录不存在: {frontend_dir}")
            return None
        
        # 启动 HTTP 服务器
        process = subprocess.Popen(
            [sys.executable, '-m', 'http.server', str(FRONTEND_PORT)],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待前端服务器启动
        print("等待前端服务启动...")
        time.sleep(3)  # 给HTTP服务器启动时间
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print(f"✅ 前端服务器已成功启动在端口 {FRONTEND_PORT}")
            return process
        else:
            print(f"❌ 前端服务器启动失败")
            return None
            
    except Exception as e:
        print(f"❌ 启动前端服务器时出错: {e}")
        return None

def main():
    print("🚀 正在启动食物营养分析应用...")
    print("=" * 50)
    
    # 检查必要的文件
    if not os.path.exists(os.path.join(backend_dir, 'app.py')):
        print("❌ 找不到 app.py 文件")
        return
    
    if not os.path.exists(frontend_dir):
        print("❌ 找不到前端目录")
        return
    
    # 启动后端
    backend_process = run_backend()
    if not backend_process:
        print("❌ 后端启动失败，应用无法继续")
        return
    
    # 启动前端
    frontend_process = run_frontend_server()
    if not frontend_process:
        print("❌ 前端启动失败，应用无法继续")
        backend_process.terminate()
        return
    
    print("=" * 50)
    print("🎉 应用启动成功！")
    print(f"📱 前端地址: http://localhost:{FRONTEND_PORT}")
    print(f"🔧 后端地址: http://localhost:{BACKEND_PORT}")
    print("=" * 50)
    
    # 打开浏览器
    try:
        url = f'http://localhost:{FRONTEND_PORT}'
        print(f"🌐 正在打开浏览器: {url}")
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器: {e}")
        print(f"请手动访问: {url}")
    
    print("\n💡 使用说明:")
    print("- 上传食物图片进行分析")
    print("- 查看营养信息和健康建议")
    print("- 按 Ctrl+C 停止应用")
    
    try:
        # 保持应用运行
        while True:
            time.sleep(1)
            # 检查进程是否还在运行
            if backend_process.poll() is not None:
                print("❌ 后端进程意外终止")
                break
            if frontend_process.poll() is not None:
                print("❌ 前端进程意外终止")
                break
    except KeyboardInterrupt:
        print("\n🛑 正在停止应用...")
    finally:
        # 清理进程
        if backend_process:
            backend_process.terminate()
            print("✅ 后端进程已停止")
        if frontend_process:
            frontend_process.terminate()
            print("✅ 前端进程已停止")
        print("👋 应用已完全停止")

if __name__ == '__main__':
    main() 