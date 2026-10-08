import streamlit as st
from ultralytics import YOLO
from PIL import Image
import time
from database import (
    init_db, get_or_create_user, save_pickup,
    get_history, get_leaderboard,
    get_user_password, set_user_password
)

# Initialize database
init_db()

# Load fast YOLOv8 model
model = YOLO('yolov8n.pt')

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="EcoLoop", page_icon="♻️", layout="centered")

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    }
    h1, h2, h3 {
        color: #4ade80 !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
    }
    p, label, .stMarkdown, .stText {
        color: #e0f2fe !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #16a34a, #4ade80);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 700;
        font-size: 16px;
        width: 100%;
        box-shadow: 0 4px 15px rgba(74, 222, 128, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 222, 128, 0.6);
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: rgba(255, 255, 255, 0.08);
        color: white !important;
        border: 2px solid #4ade80;
        border-radius: 12px;
        padding: 12px;
        font-size: 16px;
    }
    .metric-card {
        padding: 25px;
        border-radius: 18px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    .hero-banner {
        background: linear-gradient(90deg, #16a34a, #4ade80);
        padding: 30px 30px;
        border-radius: 24px;
        text-align: center;
        margin: 20px 0 30px 0;
        box-shadow: 0 12px 40px rgba(74, 222, 128, 0.4);
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.06);
        padding: 25px;
        border-radius: 18px;
        border-left: 4px solid #4ade80;
        margin: 15px 0;
        backdrop-filter: blur(10px);
    }
    .login-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 40px;
        border-radius: 24px;
        border: 2px solid rgba(74, 222, 128, 0.3);
        margin-top: 20px;
        backdrop-filter: blur(15px);
    }
    .step-indicator {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin: 30px 0;
    }
    .step-active {
        background: linear-gradient(90deg, #16a34a, #4ade80);
        color: white;
        padding: 12px 24px;
        border-radius: 50px;
        font-weight: 700;
    }
    .step-inactive {
        background: rgba(255, 255, 255, 0.08);
        color: #94a3b8;
        padding: 12px 24px;
        border-radius: 50px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE INIT ==========
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'user' not in st.session_state:
    st.session_state.user = None
if 'cart' not in st.session_state:
    st.session_state.cart = 0
if 'total' not in st.session_state:
    st.session_state.total = 0
if 'scanned_items' not in st.session_state:
    st.session_state.scanned_items = []
if 'last_pickup' not in st.session_state:
    st.session_state.last_pickup = None


# ==================================================
# PAGE 1: LOGIN
# ==================================================
if st.session_state.page == 'login':
    st.markdown("""
    <h1 style="text-align: center; color: #4ade80; font-size: 64px; margin: 20px 0 5px 0; font-weight: 900;">
        ♻️ EcoLoop
    </h1>
    <p style="text-align: center; color: #94a3b8; font-size: 15px; margin: 0 0 25px 0; letter-spacing: 2px; text-transform: uppercase;">
        Scan · Recycle · Earn
    </p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-banner">
        <p style="color: white; font-size: 24px; margin: 0; font-weight: 500;">
            Scan → Recycle → Earn
        </p>
        <p style="color: rgba(255,255,255,0.9); font-size: 16px; margin-top: 10px;">
            🏆 Aligned with UN SDG 12 — Responsible Consumption & Production
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("### 👤 Welcome to EcoLoop")
    st.markdown("Enter your name and password to access your account.")

    name_input = st.text_input("Your Name:", placeholder="e.g., Anushri Shinde")
    password_input = st.text_input("Password:", type="password", placeholder="Enter your password")

    if st.button("🚀 Start Recycling"):
        if not name_input.strip():
            st.error("Please enter your name to continue.")
        elif not password_input.strip():
            st.error("Please enter your password to continue.")
        elif len(password_input) < 4:
            st.error("Password must be at least 4 characters.")
        else:
            username = name_input.strip()
            saved_password = get_user_password(username)

            if saved_password is None:
                user = get_or_create_user(username)
                set_user_password(username, password_input)
                st.session_state.user = user
                st.session_state.page = 'scan'
                st.success(f"Welcome, {username}! Your account has been created.")
                st.rerun()
            elif saved_password == password_input:
                user = get_or_create_user(username)
                st.session_state.user = user
                st.session_state.page = 'scan'
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")

    st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# PAGE 2: SCAN
# ==================================================
elif st.session_state.page == 'scan':
    user = st.session_state.user

    st.markdown("""
    <div class="step-indicator">
        <span class="step-active">1. Scan</span>
        <span class="step-inactive">2. Address</span>
        <span class="step-inactive">3. Confirm</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 Home", key="home_top_scan"):
        st.session_state.page = 'login'
        st.session_state.user = None
        st.session_state.cart = 0
        st.session_state.total = 0
        st.session_state.scanned_items = []
        st.rerun()

    st.markdown(f"## 👋 Hi, {user['username']}!")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #16a34a, #22c55e);">
            <p style="color: white; margin: 0; font-size: 12px;">💰 TOTAL EARNED</p>
            <p style="color: white; font-size: 30px; font-weight: 800; margin: 5px 0;">₹{user['total_earned']}</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #0ea5e9, #38bdf8);">
            <p style="color: white; margin: 0; font-size: 12px;">♻️ ITEMS</p>
            <p style="color: white; font-size: 30px; font-weight: 800; margin: 5px 0;">{user['total_items']}</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b, #fbbf24);">
            <p style="color: white; margin: 0; font-size: 12px;">🏆 SCORE</p>
            <p style="color: white; font-size: 30px; font-weight: 800; margin: 5px 0;">{user['env_score']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="feature-card">
        <h3 style="margin: 0;">🛒 Cart: {st.session_state.cart} items | Total: ₹{st.session_state.total}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📷 Upload Plastic Item")
    uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        col_a, col_b = st.columns([1, 2])

        with col_a:
            st.markdown("<div style='max-width: 220px;'>", unsafe_allow_html=True)
            st.image(image, caption='Scanned Item', use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            with st.spinner('🤖 AI is detecting...'):
                results = model(image)
                detected_label = "Unknown"
                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        label = model.names[cls].lower()
                        if "bottle" in label:
                            detected_label = "bottle"
                        elif "cup" in label:
                            detected_label = "cup"
                        elif "bag" in label or "handbag" in label or "suitcase" in label:
                            detected_label = "bag"
                        elif "jar" in label:
                            detected_label = "jar"
                        elif "pen" in label:
                            detected_label = "pen"
                        if detected_label != "Unknown":
                            break
                time.sleep(1)

            # Smart fallback: read filename
            if detected_label == "Unknown":
                filename = uploaded_file.name.lower()
                if "pen" in filename:
                    detected_label = "pen"
                elif "bag" in filename:
                    detected_label = "bag"
                elif "jar" in filename:
                    detected_label = "jar"
                elif "bottle" in filename:
                    detected_label = "bottle"
                elif "cup" in filename:
                    detected_label = "cup"

            # Final fallback: dropdown
            if detected_label == "Unknown":
                st.warning("⚠️ AI could not detect clearly. Please confirm:")
                detected_label = st.selectbox(
                    "Select item:",
                    ["bottle", "cup", "bag", "jar", "pen"]
                )

            st.markdown(f"### ✅ Detected: **{detected_label.title()}**")

            # ===== UPDATED PRICES =====
            prices = {"bottle": 8, "cup": 4, "bag": 3, "jar": 10, "pen": 1}
            price = prices.get(detected_label, 0)

            if price > 0:
                st.success(f"Recyclable! You earn **₹{price}** per piece.")
                if st.button(f"➕ Add to Cart (₹{price})"):
                    st.session_state.cart += 1
                    st.session_state.total += price
                    st.session_state.scanned_items.append((detected_label, price))
                    st.rerun()

    st.markdown("---")
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("🏠 Back to Home", key="home_bottom_scan"):
            st.session_state.page = 'login'
            st.session_state.user = None
            st.session_state.cart = 0
            st.session_state.total = 0
            st.session_state.scanned_items = []
            st.rerun()

    with c2:
        if st.button("🚪 Logout"):
            st.session_state.page = 'login'
            st.session_state.user = None
            st.session_state.cart = 0
            st.session_state.total = 0
            st.session_state.scanned_items = []
            st.rerun()

    with c3:
        if st.session_state.cart >= 3:
            if st.button("➡️ Proceed to Address"):
                st.session_state.page = 'address'
                st.rerun()
        else:
            remaining = 3 - st.session_state.cart
            st.info(f"Add {remaining} more item(s).")

    with st.expander("📜 View My Recent History"):
        history = get_history(user['username'])
        if not history:
            st.info("No history yet.")
        else:
            for row in history[:5]:
                item_type, price, address, pickup_date, timestamp = row
                st.write(f"♻️ **{item_type.title()}** — ₹{price} — {timestamp}")


# ==================================================
# PAGE 3: ADDRESS
# ==================================================
elif st.session_state.page == 'address':
    user = st.session_state.user

    st.markdown("""
    <div class="step-indicator">
        <span class="step-inactive">1. Scan</span>
        <span class="step-active">2. Address</span>
        <span class="step-inactive">3. Confirm</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 Home", key="home_top_address"):
        st.session_state.page = 'login'
        st.session_state.user = None
        st.session_state.cart = 0
        st.session_state.total = 0
        st.session_state.scanned_items = []
        st.rerun()

    st.markdown("## 🏠 Pickup Details")
    st.markdown("Enter your details so our delivery partner can collect the items.")

    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 15px; margin: 20px 0; flex-wrap: wrap;">
        <div style="background: rgba(74,222,128,0.15); padding: 10px 18px; border-radius: 30px; border: 1px solid rgba(74,222,128,0.3);">
            <span style="color: #4ade80; font-size: 14px; font-weight: 600;">🔒 100% Secure</span>
        </div>
        <div style="background: rgba(14,165,233,0.15); padding: 10px 18px; border-radius: 30px; border: 1px solid rgba(14,165,233,0.3);">
            <span style="color: #38bdf8; font-size: 14px; font-weight: 600;">⚡ Same-Day Pickup</span>
        </div>
        <div style="background: rgba(245,158,11,0.15); padding: 10px 18px; border-radius: 30px; border: 1px solid rgba(245,158,11,0.3);">
            <span style="color: #fbbf24; font-size: 14px; font-weight: 600;">💰 Instant Payment</span>
        </div>
        <div style="background: rgba(139,92,246,0.15); padding: 10px 18px; border-radius: 30px; border: 1px solid rgba(139,92,246,0.3);">
            <span style="color: #a78bfa; font-size: 14px; font-weight: 600;">🌍 Carbon Neutral</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Items Being Recycled")
    items_count = {}
    for item, price in st.session_state.scanned_items:
        if item in items_count:
            items_count[item]['count'] += 1
            items_count[item]['total'] += price
        else:
            items_count[item] = {'count': 1, 'total': price, 'price': price}

    icons = {"bottle": "🍾", "cup": "🥤", "bag": "🛍️", "jar": "🫙", "pen": "🖊️"}

    for item, data in items_count.items():
        icon = icons.get(item, "♻️")
        st.markdown(f"""
        <div class="feature-card" style="margin: 8px 0; padding: 15px 20px;">
            <p style="margin: 0; font-size: 16px;">
                {icon} <b>{item.title()}</b> × {data['count']} &nbsp;&nbsp;|&nbsp;&nbsp;
                <span style="color: #4ade80;">₹{data['price']} each</span> &nbsp;&nbsp;|&nbsp;&nbsp;
                Total: <b>₹{data['total']}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="feature-card" style="background: linear-gradient(90deg, rgba(74,222,128,0.15), rgba(14,165,233,0.15));">
        <h3 style="margin: 0; text-align: center;">
            🎯 Grand Total: ₹{st.session_state.total} &nbsp;|&nbsp; {st.session_state.cart} items
        </h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    address = st.text_input("🏠 Full Address:", placeholder="e.g., A/p Umbraj, Dist. Satara")
    phone = st.text_input("📞 Phone Number:", placeholder="10-digit mobile number")
    date = st.date_input("📅 Preferred Pickup Date:")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("🏠 Home", key="home_bottom_address"):
            st.session_state.page = 'login'
            st.session_state.user = None
            st.session_state.cart = 0
            st.session_state.total = 0
            st.session_state.scanned_items = []
            st.rerun()

    with c2:
        if st.button("⬅️ Back to Scan"):
            st.session_state.page = 'scan'
            st.rerun()

    with c3:
        if st.button("✅ Confirm Pickup"):
            if not address.strip() or not phone.strip():
                st.error("Please fill in both address and phone number.")
            elif len(phone.strip()) != 10 or not phone.strip().isdigit():
                st.error("Please enter a valid 10-digit phone number.")
            else:
                new_earned, new_items, new_score = save_pickup(
                    user['username'],
                    st.session_state.scanned_items,
                    address.strip(),
                    phone.strip(),
                    date,
                    st.session_state.total
                )
                st.session_state.last_pickup = {
                    'items': st.session_state.scanned_items.copy(),
                    'amount': st.session_state.total,
                    'address': address.strip(),
                    'phone': phone.strip(),
                    'date': date,
                    'new_earned': new_earned,
                    'new_items': new_items,
                    'new_score': new_score
                }

                st.session_state.user = get_or_create_user(user['username'])
                st.session_state.cart = 0
                st.session_state.total = 0
                st.session_state.scanned_items = []

                st.session_state.page = 'confirm'
                st.rerun()


# ==================================================
# PAGE 4: CONFIRMATION
# ==================================================
elif st.session_state.page == 'confirm':
    st.markdown("""
    <div class="step-indicator">
        <span class="step-inactive">1. Scan</span>
        <span class="step-inactive">2. Address</span>
        <span class="step-active">3. Confirm</span>
    </div>
    """, unsafe_allow_html=True)

    pickup = st.session_state.last_pickup

    st.balloons()

    st.markdown("""
    <div class="hero-banner" style="background: linear-gradient(90deg, #16a34a, #22c55e);">
        <h1 style="color: white; margin: 0; font-size: 48px;">✅ Pickup Confirmed!</h1>
        <p style="color: white; font-size: 18px; margin-top: 10px;">
            Your recycling items will be collected soon.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📄 Your Receipt")

    st.markdown(f"""
    <div class="feature-card">
        <h3 style="margin-top: 0;">💰 You Earned: ₹{pickup['amount']}</h3>
        <hr style="border-color: rgba(74,222,128,0.3);">
        <p><b>🏠 Address:</b> {pickup['address']}</p>
        <p><b>📞 Phone:</b> {pickup['phone']}</p>
        <p><b>📅 Pickup Date:</b> {pickup['date']}</p>
        <p><b>📦 Items:</b> {len(pickup['items'])} items</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📦 Items Recycled")
    for item, price in pickup['items']:
        st.markdown(f"""
        <div class="feature-card" style="margin: 5px 0;">
            <p style="margin: 0; font-size: 16px;">
                ♻️ <b>{item.title()}</b> — ₹{price}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🎉 Your Updated Stats")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #16a34a, #22c55e);">
            <p style="color: white; margin: 0; font-size: 12px;">💰 LIFETIME EARNED</p>
            <p style="color: white; font-size: 28px; font-weight: 800; margin: 5px 0;">₹{pickup['new_earned']}</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #0ea5e9, #38bdf8);">
            <p style="color: white; margin: 0; font-size: 12px;">♻️ TOTAL ITEMS</p>
            <p style="color: white; font-size: 28px; font-weight: 800; margin: 5px 0;">{pickup['new_items']}</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b, #fbbf24);">
            <p style="color: white; margin: 0; font-size: 12px;">🏆 ENV. SCORE</p>
            <p style="color: white; font-size: 28px; font-weight: 800; margin: 5px 0;">{pickup['new_score']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Scan More Items"):
            st.session_state.page = 'scan'
            st.rerun()
    with c2:
        if st.button("🏠 Back to Home"):
            st.session_state.page = 'login'
            st.session_state.user = None
            st.session_state.cart = 0
            st.session_state.total = 0
            st.session_state.scanned_items = []
            st.rerun()