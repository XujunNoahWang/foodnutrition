import os
import sys
import time
import socket

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

def test_backend_startup():
    """测试后端启动"""
    print("测试后端启动...")
    
    # 检查 app.py 是否存在
    if not os.path.exists('app.py'):
        print("❌ app.py 不存在")
        return False
    
    # 检查 .env 文件
    env_file = '.env'
    if os.path.exists(env_file):
        print("✅ 找到 .env 文件")
    else:
        print("⚠️ 未找到 .env 文件")
    
    # 检查端口 5000
    if is_port_in_use(5000):
        print("⚠️ 端口 5000 已被占用")
    else:
        print("✅ 端口 5000 可用")
    
    return True

def test_frontend_startup():
    """测试前端启动"""
    print("测试前端启动...")
    
    # 检查前端目录
    frontend_dir = 'public'
    if os.path.exists(frontend_dir):
        print("✅ 前端目录存在")
        
        # 检查必要文件
        required_files = ['index.html', 'script.js', 'style.css']
        for file in required_files:
            if os.path.exists(os.path.join(frontend_dir, file)):
                print(f"✅ {file} 存在")
            else:
                print(f"❌ {file} 不存在")
    else:
        print("❌ 前端目录不存在")
        return False
    
    # 检查端口 8080
    if is_port_in_use(8080):
        print("⚠️ 端口 8080 已被占用")
    else:
        print("✅ 端口 8080 可用")
    
    return True

if __name__ == '__main__':
    print("🔍 启动环境检查...")
    print("=" * 40)
    
    backend_ok = test_backend_startup()
    print()
    frontend_ok = test_frontend_startup()
    
    print("=" * 40)
    if backend_ok and frontend_ok:
        print("✅ 环境检查通过，可以启动应用")
    else:
        print("❌ 环境检查失败，请修复问题后重试") 