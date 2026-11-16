# catalog_demo.py
# Самодостаточный демо-каталог: данные, картинки, тема, аккаунт, корзина и страницы в одном файле.
import base64
import io

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Каталог", page_icon="🛍️", layout="wide")

# ---------- Состояние сессии (демо, без базы данных) ----------
if "users" not in st.session_state:
    st.session_state.users = {"demo": "demo"}   # логин: пароль
if "user" not in st.session_state:
    st.session_state.user = None                 # текущий вошедший пользователь
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = None            # None, "login" или "register"
if "page" not in st.session_state:
    st.session_state.page = "Каталог"            # текущая страница
if "cart" not in st.session_state:
    st.session_state.cart = {}                   # id товара: количество

# ---------- Фейковые данные ----------
PRODUCTS = [
    {"id": 1, "name": "Кроссовки беговые", "category": "Спорт", "price": 4990, "old_price": 6490, "rating": 4.7, "reviews": 128},
    {"id": 2, "name": "Кофемашина капсульная", "category": "Техника", "price": 12900, "old_price": None, "rating": 4.5, "reviews": 64},
    {"id": 3, "name": "Рюкзак городской 20л", "category": "Аксессуары", "price": 2350, "old_price": 2990, "rating": 4.8, "reviews": 301},
    {"id": 4, "name": "Футболка хлопковая", "category": "Одежда", "price": 990, "old_price": 1290, "rating": 4.3, "reviews": 77},
    {"id": 5, "name": "Настольная лампа LED", "category": "Дом", "price": 1850, "old_price": None, "rating": 4.6, "reviews": 42},
    {"id": 6, "name": "Термокружка 500мл", "category": "Дом", "price": 760, "old_price": 890, "rating": 4.4, "reviews": 210},
    {"id": 7, "name": "Наушники беспроводные", "category": "Техника", "price": 5490, "old_price": 7990, "rating": 4.2, "reviews": 512},
    {"id": 8, "name": "Йога-коврик", "category": "Спорт", "price": 1400, "old_price": None, "rating": 4.9, "reviews": 88},
    {"id": 9, "name": "Худи с капюшоном", "category": "Одежда", "price": 2790, "old_price": 3390, "rating": 4.6, "reviews": 95},
    {"id": 10, "name": "Книга «Python для анализа»", "category": "Книги", "price": 1290, "old_price": None, "rating": 4.8, "reviews": 156},
    {"id": 11, "name": "Чайник электрический", "category": "Дом", "price": 2190, "old_price": 2590, "rating": 4.1, "reviews": 39},
    {"id": 12, "name": "Смарт-часы", "category": "Техника", "price": 8990, "old_price": 10990, "rating": 4.5, "reviews": 230},
]
PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS}

CATEGORY_COLORS = {
    "Спорт": (255, 138, 101),
    "Техника": (79, 195, 247),
    "Аксессуары": (174, 213, 129),
    "Одежда": (240, 98, 146),
    "Дом": (255, 213, 79),
    "Книги": (149, 117, 205),
}

# Демо-история заказов для личного кабинета
FAKE_ORDERS = [
    {"number": "№ 10482", "date": "02.11.2026", "items": "Наушники беспроводные", "total": 5490, "status": "Доставлен"},
    {"number": "№ 10317", "date": "21.10.2026", "items": "Худи с капюшоном, Футболка хлопковая", "total": 3780, "status": "Доставлен"},
    {"number": "№ 10190", "date": "05.10.2026", "items": "Йога-коврик", "total": 1400, "status": "В пути"},
]

# ---------- Темы ----------
THEMES = {
    "Дневная": {
        "bg": "#f6f7f9",        # фон страницы
        "sidebar": "#ffffff",   # боковые панели
        "card": "#ffffff",      # карточки товаров и поля ввода
        "border": "#e3e6ea",    # рамки
        "fg": "#14171a",        # основной текст
        "muted": "#6b7280",     # второстепенный текст
        "accent": "#1e88e5",    # акцент (наведение, теги, активная вкладка)
    },
    "Тёмная": {
        "bg": "#0f1115",
        "sidebar": "#161a20",
        "card": "#1b2028",
        "border": "#2a313c",
        "fg": "#eef1f5",
        "muted": "#9aa4b2",
        "accent": "#1e88e5",
    },
}


def apply_theme(theme_name: str):
    t = THEMES[theme_name]
    st.markdown(
        f"""
        <style>
        .stApp, [data-testid="stHeader"] {{
            background-color: {t['bg']} !important;
        }}
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div {{
            background-color: {t['sidebar']} !important;
        }}
        [data-testid="stSidebar"] {{
            border-right: 1px solid {t['border']};
        }}
        .stApp, .stApp p, .stApp span, .stApp label, .stApp h1,
        .stApp h2, .stApp h3, .stApp h4, .stApp li,
        [data-testid="stSidebar"] * {{
            color: {t['fg']} !important;
        }}
        [data-testid="stCaptionContainer"] * {{
            color: {t['muted']} !important;
        }}
        .ozon-brand {{
            font-size: 24px;
            font-weight: 700;
            color: {t['fg']};
            line-height: 2.4rem;
            margin: 0;
        }}

        /* Карточки товаров */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {t['card']} !important;
            border-color: {t['border']} !important;
            border-radius: 12px !important;
        }}

        /* Формы входа и регистрации */
        [data-testid="stForm"] {{
            background-color: {t['card']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 12px !important;
        }}

        /* ===== Поля ввода, выбор категорий, сортировка: все вложенные элементы ===== */
        [data-testid="stTextInputRootElement"],
        [data-testid="stTextInputRootElement"] *,
        [data-testid="stTextInput"] [data-baseweb] ,
        [data-testid="stTextInput"] [data-baseweb] *,
        [data-testid="stSelectbox"] [data-baseweb] ,
        [data-testid="stSelectbox"] [data-baseweb] *,
        [data-testid="stMultiSelect"] [data-baseweb],
        [data-testid="stMultiSelect"] [data-baseweb] * {{
            background-color: {t['card']} !important;
            color: {t['fg']} !important;
            -webkit-text-fill-color: {t['fg']} !important;
        }}
        [data-testid="stTextInputRootElement"],
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div {{
            border: 1px solid {t['border']} !important;
            border-radius: 8px !important;
        }}
        input::placeholder {{
            color: {t['muted']} !important;
            -webkit-text-fill-color: {t['muted']} !important;
        }}
        [data-baseweb="select"] svg {{
            fill: {t['muted']} !important;
        }}

        /* Теги выбранных категорий */
        [data-testid="stMultiSelect"] [data-baseweb="tag"],
        [data-testid="stMultiSelect"] [data-baseweb="tag"] * {{
            background-color: {t['accent']} !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            fill: #ffffff !important;
        }}

        /* Раскрытый список вариантов */
        [data-baseweb="popover"],
        [data-baseweb="popover"] *,
        [data-baseweb="menu"],
        [data-baseweb="menu"] * {{
            background-color: {t['card']} !important;
            color: {t['fg']} !important;
            -webkit-text-fill-color: {t['fg']} !important;
        }}
        [data-baseweb="popover"] li:hover,
        [data-baseweb="popover"] li:hover *,
        [data-baseweb="popover"] li[aria-selected="true"],
        [data-baseweb="popover"] li[aria-selected="true"] * {{
            background-color: {t['bg']} !important;
        }}

        /* Кнопки: белые, при наведении цвет акцента */
        .stApp .stButton > button,
        .stApp .stFormSubmitButton > button {{
            background-color: #ffffff !important;
            border: 1px solid {t['border']} !important;
            transition: background-color 0.15s, border-color 0.15s;
        }}
        .stApp .stButton > button p,
        .stApp .stFormSubmitButton > button p {{
            color: #111111 !important;
        }}
        .stApp .stButton > button:hover,
        .stApp .stFormSubmitButton > button:hover {{
            background-color: {t['accent']} !important;
            border-color: {t['accent']} !important;
        }}
        .stApp .stButton > button:hover p,
        .stApp .stFormSubmitButton > button:hover p {{
            color: #ffffff !important;
        }}

        /* Активная вкладка верхней панели (primary): синяя с белым текстом */
        .stApp .stButton > button[kind="primary"],
        .stApp .stButton > button[data-testid="stBaseButton-primary"] {{
            background-color: {t['accent']} !important;
            border-color: {t['accent']} !important;
        }}
        .stApp .stButton > button[kind="primary"] p,
        .stApp .stButton > button[data-testid="stBaseButton-primary"] p {{
            color: #ffffff !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------- Навигация ----------
PAGES = ["Каталог", "Корзина", "Личный кабинет"]


def go_to(page: str):
    st.session_state.page = page


def cart_count() -> int:
    return sum(st.session_state.cart.values())


def render_nav():
    """Верхняя панель: название сайта и кнопки перехода между страницами."""
    brand, c1, c2, c3, _ = st.columns([2, 1, 1, 1.3, 3])
    brand.markdown('<div class="ozon-brand">Ozon4ik</div>', unsafe_allow_html=True)

    labels = {
        "Каталог": "Каталог",
        "Корзина": f"Корзина ({cart_count()})" if cart_count() else "Корзина",
        "Личный кабинет": "Личный кабинет",
    }
    for col, page in zip([c1, c2, c3], PAGES):
        col.button(
            labels[page],
            key=f"nav_{page}",
            use_container_width=True,
            type="primary" if st.session_state.page == page else "secondary",
            on_click=go_to,
            args=(page,),
        )
    st.divider()


# ---------- Аккаунт: кнопки и форма ----------
def render_auth_buttons():
    """Кнопки в правой колонке: либо вход/регистрация, либо имя и выход."""
    if st.session_state.user:
        st.markdown(f"**{st.session_state.user}**")
        if st.button("Выйти", use_container_width=True):
            st.session_state.user = None
            st.rerun()
        return

    if st.button("Войти", use_container_width=True):
        st.session_state.auth_mode = "login"
    if st.button("Регистрация", use_container_width=True):
        st.session_state.auth_mode = "register"


def render_auth_form():
    """Форма входа или регистрации, открывается по нажатию кнопки."""
    mode = st.session_state.auth_mode
    if mode is None or st.session_state.user:
        return

    title = "Вход" if mode == "login" else "Регистрация"
    with st.form(f"{mode}_form", clear_on_submit=False):
        st.subheader(title)
        login = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button(title, use_container_width=True)

    if submitted:
        if not login or not password:
            st.warning("Заполни логин и пароль.")
        elif mode == "register":
            if login in st.session_state.users:
                st.error("Такой логин уже занят.")
            else:
                st.session_state.users[login] = password
                st.session_state.user = login
                st.session_state.auth_mode = None
                st.rerun()
        else:  # login
            if st.session_state.users.get(login) == password:
                st.session_state.user = login
                st.session_state.auth_mode = None
                st.rerun()
            else:
                st.error("Неверный логин или пароль.")


# ---------- Картинки в памяти ----------
def load_font(size: int):
    for path in [
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


@st.cache_data
def product_image_uri(name: str, category: str) -> str:
    """Рисует картинку-заглушку и возвращает её как data-URI (без файлов на диске)."""
    img = Image.new("RGB", (400, 400), CATEGORY_COLORS.get(category, (200, 200, 200)))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((30, 120, 370, 280), radius=24, fill=(255, 255, 255))

    font_big, font_small = load_font(30), load_font(20)
    lines, line = [], ""
    for word in name.split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=font_big) <= 330:
            line = test
        else:
            lines.append(line)
            line = word
    lines.append(line)

    y = 150 if len(lines) == 1 else 135
    for ln in lines:
        draw.text((200, y), ln, fill=(40, 40, 40), font=font_big, anchor="mm")
        y += 40
    draw.text((200, 320), category, fill=(255, 255, 255), font=font_small, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


# ---------- Корзина ----------
def fmt_price(value: float) -> str:
    return f"{value:,.0f} ₽".replace(",", " ")


def add_to_cart(pid: int):
    p = PRODUCTS_BY_ID[pid]
    if not st.session_state.user:
        st.toast("Чтобы добавить в корзину, войди в аккаунт")
        return
    st.session_state.cart[pid] = st.session_state.cart.get(pid, 0) + 1
    st.toast(f"«{p['name']}» добавлен в корзину")


def remove_from_cart(pid: int):
    st.session_state.cart.pop(pid, None)


def clear_cart():
    st.session_state.cart = {}


# ---------- Страница: каталог ----------
def render_card(p: dict):
    with st.container(border=True):
        st.markdown(
            f"<img src='{product_image_uri(p['name'], p['category'])}' style='width:100%;border-radius:8px'>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**{p['name']}**")
        st.caption(f"{p['category']} · ★ {p['rating']} ({p['reviews']})")

        if p["old_price"]:
            discount = round((1 - p["price"] / p["old_price"]) * 100)
            st.markdown(f"~~{fmt_price(p['old_price'])}~~ **{fmt_price(p['price'])}** :red[-{discount}%]")
        else:
            st.markdown(f"**{fmt_price(p['price'])}**")

        st.button(
            "В корзину",
            key=f"add_{p['id']}",
            use_container_width=True,
            on_click=add_to_cart,
            args=(p["id"],),
        )


def render_catalog_page():
    # Фильтры в левой боковой панели (только на странице каталога)
    with st.sidebar:
        st.subheader("Фильтры")
        categories = sorted({p["category"] for p in PRODUCTS})
        selected = st.multiselect("Категория", categories, default=categories)
        max_price = max(p["price"] for p in PRODUCTS)
        price_range = st.slider("Цена, ₽", 0, max_price, (0, max_price), step=100)
        sort_by = st.selectbox(
            "Сортировка",
            ["По популярности", "Цена: по возрастанию", "Цена: по убыванию", "Рейтинг"],
        )
        search = st.text_input("Поиск по названию")

    items = [
        p for p in PRODUCTS
        if p["category"] in selected
        and price_range[0] <= p["price"] <= price_range[1]
        and search.lower() in p["name"].lower()
    ]

    sort_keys = {
        "По популярности": (lambda p: p["reviews"], True),
        "Цена: по возрастанию": (lambda p: p["price"], False),
        "Цена: по убыванию": (lambda p: p["price"], True),
        "Рейтинг": (lambda p: p["rating"], True),
    }
    key, reverse = sort_keys[sort_by]
    items = sorted(items, key=key, reverse=reverse)

    st.header("Каталог товаров")
    st.caption("Демонстрационные данные, не из датасетов проекта")
    st.write(f"Найдено товаров: **{len(items)}**")

    if not items:
        st.info("По выбранным фильтрам ничего не найдено.")
        return

    cols_per_row = 4
    for i in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, product in zip(cols, items[i:i + cols_per_row]):
            with col:
                render_card(product)


# ---------- Страница: корзина ----------
def render_cart_page():
    st.header("Корзина")

    if not st.session_state.cart:
        st.info("Корзина пуста. Добавь товары на странице «Каталог».")
        st.button("Перейти в каталог", on_click=go_to, args=("Каталог",))
        return

    total = 0
    for pid, qty in st.session_state.cart.items():
        p = PRODUCTS_BY_ID[pid]
        line_total = p["price"] * qty
        total += line_total
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([4, 1, 2, 1.5])
            c1.markdown(f"**{p['name']}**")
            c1.caption(p["category"])
            c2.markdown(f"× {qty}")
            c3.markdown(f"**{fmt_price(line_total)}**")
            c4.button("Удалить", key=f"rm_{pid}", use_container_width=True,
                      on_click=remove_from_cart, args=(pid,))

    st.markdown(f"### Итого: {fmt_price(total)}")
    b1, b2, _ = st.columns([1.5, 1.5, 4])
    if b1.button("Оформить заказ", use_container_width=True):
        st.toast("Оформление заказа в демо не реализовано")
    b2.button("Очистить", use_container_width=True, on_click=clear_cart)


# ---------- Страница: личный кабинет ----------
def render_account_page():
    st.header("Личный кабинет")

    if not st.session_state.user:
        st.info("Войди или зарегистрируйся с помощью кнопок справа, чтобы увидеть личный кабинет.")
        return

    with st.container(border=True):
        st.subheader(st.session_state.user)
        st.caption("Демо-профиль, данные хранятся только в текущей сессии")
        m1, m2, m3 = st.columns(3)
        m1.metric("Товаров в корзине", cart_count())
        m2.metric("Заказов", len(FAKE_ORDERS))
        m3.metric("Потрачено", fmt_price(sum(o["total"] for o in FAKE_ORDERS)))

    st.subheader("История заказов")
    for o in FAKE_ORDERS:
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 5, 2])
            c1.markdown(f"**{o['number']}**")
            c1.caption(o["date"])
            c2.markdown(o["items"])
            c3.markdown(f"**{fmt_price(o['total'])}**")
            c3.caption(o["status"])


# ---------- Сборка приложения ----------
def render_app():
    render_nav()

    # Основная область и правая панель
    main, right = st.columns([5, 1])

    with right:
        render_auth_buttons()
        st.divider()
        st.subheader("Тема")
        theme_name = st.radio("Тема", list(THEMES.keys()), label_visibility="collapsed")

    apply_theme(theme_name)

    with main:
        render_auth_form()
        page = st.session_state.page
        if page == "Каталог":
            render_catalog_page()
        elif page == "Корзина":
            render_cart_page()
        else:
            render_account_page()


render_app()
