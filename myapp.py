# catalog_demo.py
# Самодостаточный демо-каталог: данные, картинки, тема и страница в одном файле.
import base64
import io

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Каталог", page_icon="🛍️", layout="wide")

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

CATEGORY_COLORS = {
    "Спорт": (255, 138, 101),
    "Техника": (79, 195, 247),
    "Аксессуары": (174, 213, 129),
    "Одежда": (240, 98, 146),
    "Дом": (255, 213, 79),
    "Книги": (149, 117, 205),
}

# ---------- Темы ----------
THEMES = {
    "Дневная": {"bg": "#ffffff", "sidebar": "#f5f5f5", "fg": "#111111"},
    "Тёмная": {"bg": "#000000", "sidebar": "#121212", "fg": "#f5f5f5"},
}


def apply_theme(theme_name: str):
    t = THEMES[theme_name]
    st.markdown(
        f"""
        <style>
        .stApp, [data-testid="stHeader"] {{
            background-color: {t['bg']} !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: {t['sidebar']} !important;
        }}
        .stApp, .stApp p, .stApp span, .stApp label, .stApp h1,
        .stApp h2, .stApp h3, .stApp h4, .stApp li,
        [data-testid="stSidebar"] * {{
            color: {t['fg']} !important;
        }}
        .ozon-brand {{
            font-size: 62px;
            font-weight: 700;
            color: {t['fg']};
            margin: 0 0 8px 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


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


# ---------- Карточка и страница ----------
def fmt_price(value: float) -> str:
    return f"{value:,.0f} ₽".replace(",", " ")


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

        if st.button("В корзину", key=f"add_{p['id']}", use_container_width=True):
            st.toast(f"«{p['name']}» добавлен (демо)")


def render_catalog():
    # Основная область и правая панель
    main, right = st.columns([5, 1])

    with right:
        st.subheader("Тема")
        theme_name = st.radio("Тема", list(THEMES.keys()), label_visibility="collapsed")

    apply_theme(theme_name)

    # Фильтры в левой боковой панели
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

    with main:
        st.markdown('<div class="ozon-brand">Ozon4ik</div>', unsafe_allow_html=True)
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


render_catalog()