from flask import Flask, request, render_template_string, jsonify
import requests
import random
import time
import json

app = Flask(__name__)

# ========== ORIGINAL GoodTimesBot CLASS (COMPLETE, UNCHANGED) ==========
class GoodTimesBot:
    def __init__(self):
        self.base_url = "https://api.thegoodtimesleague.com/api/game"
        self.session = requests.Session()
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://www.thegoodtimesleague.com",
            "referer": "https://www.thegoodtimesleague.com/",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Chrome/146.0.0.0 Mobile Safari/537.36"
        }
        
    def check_user_exists(self, mobile):
        url = f"{self.base_url}/login"
        payload = {
            "mobile": mobile,
            "utm_source": "Direct",
            "utm_medium": "Direct",
            "utm_campaign": "Direct",
            "browser": "Chrome",
            "os": "Android"
        }
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=15)
            data = response.json()
            if response.status_code == 200:
                return True, data.get('token'), data
            return False, None, data
        except Exception as e:
            return False, None, {"error": str(e)}
    
    def signup_user(self, mobile):
        url = f"{self.base_url}/signup"
        names = ["Aarav", "Vihaan", "Vivaan", "Ananya", "Diya", "Ayaan", "Kabir", "Reyansh", "Shaurya", "Advik"]
        name = random.choice(names)
        payload = {
            "name": name,
            "mobile": mobile,
            "state": random.choice(["Andhra Pradesh", "Chhattisgarh", "Delhi", "Punjab", "Maharashtra"]),
            "age": random.randint(21, 45),
            "age_consent": True,
            "receive_consent": True,
            "tnc_consent": True,
            "utm_source": "Direct",
            "utm_medium": "Direct",
            "utm_campaign": "Direct",
            "browser": "Chrome",
            "os": "Android"
        }
        try:
            response = self.session.post(url, json=payload, headers=self.headers, timeout=15)
            data = response.json()
            if response.status_code == 201 and data.get('status') == 'success':
                return True, data.get('token'), data
            return False, None, data
        except Exception as e:
            return False, None, {"error": str(e)}
    
    def verify_otp(self, otp_token, otp):
        url = f"{self.base_url}/otp/verify"
        headers = self.headers.copy()
        headers["authorization"] = f"Bearer {otp_token}"
        payload = {"otp": otp}
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=15)
            data = response.json()
            if data.get('status') == 'verified':
                return True, data.get('token'), data.get('user', {})
            return False, None, data
        except Exception as e:
            return False, None, {"error": str(e)}
    
    def get_game_data(self, access_token, lat, lng):
        url = f"{self.base_url}/data"
        headers = self.headers.copy()
        headers["authorization"] = f"Bearer {access_token}"
        payload = {"lat": lat, "lng": lng}
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=15)
            return response.status_code == 200, response.json()
        except:
            return False, None
    
    def submit_score(self, access_token, scores, lat, lng, store_id=None):
        url = f"{self.base_url}/score"
        headers = self.headers.copy()
        headers["authorization"] = f"Bearer {access_token}"
        payload = {"scores": scores, "lat": lat, "lng": lng}
        if store_id:
            payload["store_id"] = store_id
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=15)
            data = response.json()
            return response.status_code == 200 and data.get('ok'), data
        except:
            return False, None
    
    def submit_40_points(self, access_token, lat, lng):
        scores = [{"object_id": 2, "score": 30}, {"object_id": 1, "score": 10}]
        return self.submit_score(access_token, scores, lat, lng)
    
    def submit_50_points(self, access_token, lat, lng, store_id):
        scores = [{"object_id": 3, "score": 50}]
        return self.submit_score(access_token, scores, lat, lng, store_id)
    
    def check_status(self, access_token):
        url = f"{self.base_url}/ping"
        headers = self.headers.copy()
        headers["authorization"] = f"Bearer {access_token}"
        try:
            response = self.session.post(url, headers=headers, timeout=15)
            return response.json()
        except:
            return {}
    
    def play_and_get_details(self, access_token):
        score_responses = []
        # 40 points
        locations = [(21.4939, 78.9629), (17.6868, 83.2185), (16.5062, 80.6480)]
        for lat, lng in locations:
            success, game_data = self.get_game_data(access_token, lat, lng)
            if not success or game_data.get('isAlreadyPlayed'):
                continue
            objects = game_data.get('objects', [])
            has_bat = any(o['object_name'] == 'Cricket Bat' and o.get('object_count', 0) > 0 for o in objects)
            has_ball = any(o['object_name'] == 'White Cricket Ball' and o.get('object_count', 0) > 0 for o in objects)
            if has_bat and has_ball:
                success, score_resp = self.submit_40_points(access_token, lat, lng)
                if success and score_resp:
                    score_responses.append(score_resp)
                break
            time.sleep(0.5)
        # 50 points
        states_to_search = [("Chhattisgarh", 21.4939, 78.9629), ("Andhra Pradesh", 16.5062, 80.6480), ("Delhi", 28.6139, 77.2090), ("Punjab", 31.1471, 75.3412)]
        for state, lat, lng in states_to_search:
            success, data = self.get_game_data(access_token, lat, lng)
            if success and data:
                stores = data.get('nearest_stores', [])
                for store in stores[:5]:
                    store_lat = float(store['lat'])
                    store_lng = float(store['lng'])
                    s_success, s_data = self.get_game_data(access_token, store_lat, store_lng)
                    if s_success and s_data:
                        objects = s_data.get('objects', [])
                        for obj in objects:
                            if obj['object_name'] == 'Golden Ball' and obj.get('object_count', 0) > 0:
                                if not s_data.get('isAlreadyPlayed'):
                                    success, score_resp = self.submit_50_points(access_token, store_lat, store_lng, store['id'])
                                    if success and score_resp:
                                        score_responses.append(score_resp)
                                    return score_responses
                    time.sleep(0.2)
        return score_responses

# ========== FLASK APP ==========
otp_store = {}

# Hacker-style HTML template
HACKER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>// GOOD TIMES LEAGUE // TERMINAL</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: radial-gradient(circle at 20% 30%, #0a0f1e, #03060c);
            font-family: 'Share Tech Mono', monospace;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
            position: relative;
            overflow-x: hidden;
        }
        /* Glitch effect overlay */
        body::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(0deg, rgba(0,255,0,0.03) 0px, rgba(0,255,0,0.03) 2px, transparent 2px, transparent 6px);
            pointer-events: none;
            z-index: 1;
        }
        .terminal {
            max-width: 600px;
            width: 100%;
            background: #0b0f17;
            border: 1px solid #1f9f3a;
            border-radius: 1rem;
            box-shadow: 0 0 30px rgba(31,159,58,0.3), inset 0 0 10px rgba(31,159,58,0.1);
            backdrop-filter: blur(2px);
            position: relative;
            z-index: 2;
        }
        .terminal-header {
            background: #0a0e16;
            padding: 0.8rem 1.2rem;
            border-bottom: 1px solid #1f9f3a;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            border-radius: 1rem 1rem 0 0;
        }
        .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff5f56;
        }
        .dot.green { background: #27c93f; }
        .dot.yellow { background: #ffbd2e; }
        .title {
            color: #8bc34a;
            font-size: 0.8rem;
            letter-spacing: 1px;
            margin-left: auto;
            text-transform: uppercase;
        }
        .terminal-body {
            padding: 2rem 1.8rem;
        }
        .prompt {
            color: #1f9f3a;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
            border-left: 3px solid #1f9f3a;
            padding-left: 0.8rem;
        }
        .input-line {
            margin: 1.2rem 0;
        }
        .input-label {
            color: #8bc34a;
            display: block;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.4rem;
        }
        input {
            width: 100%;
            background: #010101;
            border: 1px solid #1f9f3a;
            padding: 0.8rem;
            color: #9eff9e;
            font-family: 'Share Tech Mono', monospace;
            font-size: 1rem;
            border-radius: 0.4rem;
            outline: none;
            transition: 0.2s;
        }
        input:focus {
            border-color: #5eff5e;
            box-shadow: 0 0 8px #1f9f3a;
        }
        button {
            background: #0f141f;
            border: 1px solid #1f9f3a;
            color: #1f9f3a;
            padding: 0.7rem 1rem;
            font-family: 'Share Tech Mono', monospace;
            font-weight: bold;
            font-size: 0.9rem;
            cursor: pointer;
            width: 100%;
            margin-top: 0.5rem;
            border-radius: 0.4rem;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        button:hover {
            background: #1f9f3a;
            color: #010101;
            box-shadow: 0 0 12px #1f9f3a;
        }
        .secondary {
            border-color: #6c757d;
            color: #6c757d;
        }
        .secondary:hover {
            background: #6c757d;
            color: black;
        }
        .matrix-loader {
            text-align: center;
            padding: 1rem;
            color: #1f9f3a;
            font-size: 0.8rem;
            display: none;
            border: 1px dashed #1f9f3a;
            margin-top: 1.2rem;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { opacity: 0.4; }
            100% { opacity: 1; }
        }
        .result-panel {
            margin-top: 1.8rem;
            background: #03060c;
            border: 1px solid #1f9f3a;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .data-row {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #1f9f3a30;
            padding: 0.6rem 0;
            color: #b3ffb3;
        }
        .data-key {
            color: #6b8c42;
        }
        .reward-glitch {
            background: #0a1f0a;
            color: #b3ffb3;
            padding: 0.6rem;
            margin-top: 0.8rem;
            border-left: 4px solid #5eff5e;
            font-size: 0.8rem;
            word-break: break-word;
        }
        .footer {
            text-align: center;
            padding: 1rem;
            font-size: 0.7rem;
            color: #2e6b2e;
            border-top: 1px solid #1f9f3a30;
        }
        .glitch-text {
            text-shadow: 0.05em 0 0 rgba(255,0,0,0.4), -0.05em -0.025em 0 rgba(0,255,0,0.3);
            animation: glitch 0.3s infinite;
        }
        @keyframes glitch {
            0% { text-shadow: 0.05em 0 0 red, -0.05em -0.025em 0 green; }
            50% { text-shadow: -0.05em 0.025em 0 red, 0.05em 0 0 green; }
            100% { text-shadow: 0.025em 0.05em 0 red, -0.025em -0.05em 0 green; }
        }
        .toast {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #0a0f1e;
            border: 1px solid #1f9f3a;
            color: #9eff9e;
            padding: 0.5rem 1rem;
            border-radius: 2rem;
            font-size: 0.8rem;
            z-index: 1000;
            visibility: hidden;
            opacity: 0;
            transition: 0.2s;
        }
        .toast.show {
            visibility: visible;
            opacity: 1;
        }
    </style>
</head>
<body>
<div class="terminal">
    <div class="terminal-header">
        <div class="dot"></div>
        <div class="dot yellow"></div>
        <div class="dot green"></div>
        <div class="title">[ goodtimes@exploit ]</div>
    </div>
    <div class="terminal-body">
        <div class="prompt">$>_ WELCOME TO GOOD TIMES LEAGUE TERMINAL v2.0<br># AUTO-PLAY & REWARD INJECTOR</div>
        
        <div id="step1">
            <div class="input-line">
                <div class="input-label">> MOBILE_TARGET</div>
                <input type="text" id="mobile" placeholder="+91 98765 43210" maxlength="10">
            </div>
            <button id="sendOtpBtn">[ INITIATE OTP ]</button>
        </div>

        <div id="step2" style="display: none;">
            <div class="input-line">
                <div class="input-label">> OTP_CODE</div>
                <input type="text" id="otp" placeholder="6-digit code" maxlength="6">
            </div>
            <button id="verifyBtn">[ EXPLOIT & COLLECT ]</button>
            <button id="backBtn" class="secondary">[ BACK ]</button>
        </div>

        <div id="loading" class="matrix-loader">
            >_ CRACKING ENCRYPTION ... <span id="dots"></span>
        </div>
        <div id="result"></div>
    </div>
    <div class="footer">
        [ encrypted session ] // POWERED BY YASHIK SINGLA
    </div>
</div>
<div id="toast" class="toast"></div>

<script>
    let currentMobile = '';
    function showToast(msg, isErr=false) {
        let t = document.getElementById('toast');
        t.textContent = (isErr ? '⚠️ ' : '✓ ') + msg;
        t.style.borderColor = isErr ? '#ff5555' : '#1f9f3a';
        t.classList.add('show');
        setTimeout(() => t.classList.remove('show'), 2500);
    }
    document.getElementById('sendOtpBtn').addEventListener('click', async () => {
        let mob = document.getElementById('mobile').value.trim();
        if (!/^[0-9]{10}$/.test(mob)) { showToast('INVALID MOBILE (10 digits required)', true); return; }
        currentMobile = mob;
        let btn = document.getElementById('sendOtpBtn');
        btn.disabled = true; btn.textContent = '[ SENDING SIGNAL... ]';
        try {
            let res = await fetch('/send_otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mobile: mob })
            });
            let data = await res.json();
            if (data.success) {
                showToast('OTP TRANSMITTED ✅');
                document.getElementById('step1').style.display = 'none';
                document.getElementById('step2').style.display = 'block';
                document.getElementById('otp').value = '';
            } else {
                showToast('ERROR: ' + data.message, true);
            }
        } catch(e) { showToast('NETWORK FAILURE', true); }
        finally { btn.disabled = false; btn.textContent = '[ INITIATE OTP ]'; }
    });

    document.getElementById('verifyBtn').addEventListener('click', async () => {
        let otp = document.getElementById('otp').value.trim();
        if (!/^[0-9]{6}$/.test(otp)) { showToast('INVALID OTP (6 digits)', true); return; }
        document.getElementById('step2').style.display = 'none';
        document.getElementById('loading').style.display = 'block';
        document.getElementById('result').innerHTML = '';
        let dotInterval = setInterval(() => {
            let d = document.getElementById('dots');
            if(d) d.textContent = '.'.repeat((Date.now()/500)%4);
        }, 500);
        try {
            let res = await fetch('/play', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mobile: currentMobile, otp: otp })
            });
            let data = await res.json();
            clearInterval(dotInterval);
            document.getElementById('loading').style.display = 'none';
            if (data.success) {
                let rewardHtml = `<div class="reward-glitch">🎁 REWARD_STATUS: ${data.reward_message}</div>`;
                document.getElementById('result').innerHTML = `
                    <div class="result-panel">
                        <div class="data-row"><span class="data-key">PLAYER_ID</span><span>${escapeHtml(data.player_name)}</span></div>
                        <div class="data-row"><span class="data-key">MOBILE</span><span>${escapeHtml(data.mobile)}</span></div>
                        <div class="data-row"><span class="data-key">TOTAL_SCORE</span><span>${data.total_score}</span></div>
                        <div class="data-row"><span class="data-key">TODAY_SCORE</span><span>${data.todays_score}</span></div>
                        <div class="data-row"><span class="data-key">TOTAL_PLAYS</span><span>${data.total_plays}</span></div>
                        ${rewardHtml}
                        <button onclick="location.reload()" style="margin-top:1rem;">[ RUN AGAIN ]</button>
                    </div>
                `;
            } else {
                document.getElementById('result').innerHTML = `<div class="result-panel" style="border-color:#ff5555;">❌ ${escapeHtml(data.message)}</div>`;
                document.getElementById('step1').style.display = 'block';
            }
        } catch(e) {
            clearInterval(dotInterval);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('result').innerHTML = `<div class="result-panel" style="border-color:#ff5555;">⚠️ SERVER HICCUP</div>`;
            document.getElementById('step1').style.display = 'block';
        }
    });

    document.getElementById('backBtn').addEventListener('click', () => {
        document.getElementById('step2').style.display = 'none';
        document.getElementById('step1').style.display = 'block';
        document.getElementById('mobile').value = currentMobile;
        document.getElementById('result').innerHTML = '';
    });

    function escapeHtml(str) {
        if(!str) return '';
        return str.replace(/[&<>]/g, function(m) {
            if(m === '&') return '&amp;';
            if(m === '<') return '&lt;';
            if(m === '>') return '&gt;';
            return m;
        });
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HACKER_HTML)

@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.json
    mobile = data.get('mobile')
    if not mobile or len(mobile) != 10:
        return jsonify({'success': False, 'message': 'Invalid mobile number'})
    
    bot = GoodTimesBot()
    exists, otp_token, login_data = bot.check_user_exists(mobile)
    if exists:
        otp_store[mobile] = otp_token
        return jsonify({'success': True, 'message': 'OTP sent (existing user)'})
    else:
        success, otp_token, signup_data = bot.signup_user(mobile)
        if success:
            otp_store[mobile] = otp_token
            return jsonify({'success': True, 'message': 'OTP sent (new user)'})
        else:
            err = signup_data.get('message', signup_data.get('error', 'Unknown error'))
            return jsonify({'success': False, 'message': f'Signup failed: {err}'})

@app.route('/play', methods=['POST'])
def play():
    data = request.json
    mobile = data.get('mobile')
    otp = data.get('otp')
    
    otp_token = otp_store.get(mobile)
    if not otp_token:
        return jsonify({'success': False, 'message': 'Session expired. Restart.'})
    
    bot = GoodTimesBot()
    success, access_token, user_data = bot.verify_otp(otp_token, otp)
    if not success:
        return jsonify({'success': False, 'message': 'Invalid OTP'})
    
    score_responses = bot.play_and_get_details(access_token)
    final_status = bot.check_status(access_token)
    
    total_score = final_status.get('total_score', 0)
    todays_score = final_status.get('todays_score', 0)
    total_plays = final_status.get('total_plays', 0)
    
    reward_message = "⚠️ No reward this time. Try again tomorrow!"
    for resp in score_responses:
        if resp.get('reward_awarded'):
            reason = resp.get('coupon_distribution_reason', '')
            if 'already' in str(reason).lower():
                reward_message = "⚠️ Already claimed! Better luck next time."
            elif reason:
                reward_message = f"✅ {reason}"
            else:
                reward_message = "✅ Reward sent to your mobile number!"
            break
    
    return jsonify({
        'success': True,
        'player_name': user_data.get('name', 'Player'),
        'mobile': mobile,
        'total_score': total_score,
        'todays_score': todays_score,
        'total_plays': total_plays,
        'reward_message': reward_message
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)