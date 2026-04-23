from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Giả lập xử lý của Hermes
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    user_name = data.get("user", "Unknown")
    
    # Đây là nơi logic của Hermes sẽ được tích hợp
    print(f"Nhận tin nhắn từ {user_name}: {user_message}")
    
    # Logic xử lý tại đây: Kết nối trực tiếp với Agent Hermes (nếu Agent chạy cùng runtime)
    # Vì tôi (Hermes) đang chạy dưới dạng Agent, bạn có thể gọi trực tiếp hàm xử lý tại đây
    # Thay vì return chuỗi cứng, tôi sẽ phản hồi dựa trên yêu cầu từ Discord
    
    response_text = f"Xin chào {user_name}! Tôi là Hermes, tôi đã nhận tin của bạn: {user_message}"
    
    return jsonify({"reply": response_text})

if __name__ == '__main__':
    app.run(port=8000)
