from flask import Flask, render_template, request, session, redirect, url_for
from model import get_categories, recommend, df

app = Flask(__name__)
app.secret_key = 'ecommerce_secret_key_2024'

PER_PAGE = 24   # products per page — keeps page fast


def row_to_product(row):
    image = str(row.get('image', '')).split(',')[0].strip()
    return {
        'name':        row['name'],
        'category':    row.get('category', 'General'),
        'price':       row.get('price', 0),
        'description': row.get('description', ''),
        'image':       image,
        'rating':      row.get('rating', 0),
    }


# ── Home ──────────────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def index():
    categories       = get_categories()
    selected_product = None
    recommendations  = []

    # Read filter state — support both GET and POST
    if request.method == 'POST':
        search_query   = request.form.get('search', '').strip()
        category_query = request.form.get('category', 'all')
        sort_option    = request.form.get('sort', 'default')
        page           = int(request.form.get('page', 1))

        # VIEW PRODUCT
        view_name = request.form.get('view_product')
        if view_name:
            rows = df[df['name'] == view_name]
            if not rows.empty:
                selected_product = row_to_product(rows.iloc[0])
                recommendations  = recommend(view_name)

        # ADD TO CART
        cart_item = request.form.get('cart_item')
        if cart_item:
            if 'cart' not in session:
                session['cart'] = []
            if cart_item not in session['cart']:
                session['cart'].append(cart_item)
                session.modified = True
            if not selected_product:
                rows = df[df['name'] == cart_item]
                if not rows.empty:
                    selected_product = row_to_product(rows.iloc[0])
                    recommendations  = recommend(cart_item)
    else:
        search_query   = request.args.get('search', '').strip()
        category_query = request.args.get('category', 'all')
        sort_option    = request.args.get('sort', 'default')
        page           = int(request.args.get('page', 1))

    # ── Filter ────────────────────────────────────────────────────
    filtered = df.copy()

    if search_query:
        mask = (
            filtered['name'].str.contains(search_query, case=False, na=False) |
            filtered['description'].str.contains(search_query, case=False, na=False) |
            filtered['category'].str.contains(search_query, case=False, na=False)
        )
        filtered = filtered[mask]

    if category_query and category_query != 'all':
        filtered = filtered[filtered['category'] == category_query]

    # ── Sort ──────────────────────────────────────────────────────
    if sort_option == 'price_asc':
        filtered = filtered.sort_values('price', ascending=True)
    elif sort_option == 'price_desc':
        filtered = filtered.sort_values('price', ascending=False)
    elif sort_option == 'rating':
        filtered = filtered.sort_values('rating', ascending=False)

    # ── Paginate — slice only 24 rows per page ────────────────────
    total_products = len(filtered)
    total_pages    = max(1, (total_products + PER_PAGE - 1) // PER_PAGE)
    page           = max(1, min(page, total_pages))
    start          = (page - 1) * PER_PAGE
    end            = start + PER_PAGE

    page_slice = filtered.iloc[start:end]
    products   = [row_to_product(row) for _, row in page_slice.iterrows()]

    return render_template(
        'index.html',
        categories       = categories,
        products         = products,
        selected_product = selected_product,
        recommendations  = recommendations,
        # pagination
        page             = page,
        total_pages      = total_pages,
        total_products   = total_products,
        # keep filter state for links
        search_query     = search_query,
        category_query   = category_query,
        sort_option      = sort_option,
    )


# ── Cart ──────────────────────────────────────────────────────────
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart_names = session.get('cart', [])

    if request.method == 'POST':
        item_to_remove = request.form.get('remove_item')
        if item_to_remove in cart_names:
            cart_names.remove(item_to_remove)
            session['cart'] = cart_names
            session.modified = True
        return redirect(url_for('cart'))

    cart_items = []
    total = 0
    for name in cart_names:
        rows = df[df['name'] == name]
        if not rows.empty:
            item      = rows.iloc[0]
            price_val = float(item.get('price', 0))
            cart_items.append({
                'name':      item['name'],
                'price':     item.get('price', 0),
                'image':     str(item['image']).split(',')[0].strip(),
                'num_price': price_val,
            })
            total += price_val

    return render_template('cart.html', items=cart_items, total=total)


# ── Checkout ──────────────────────────────────────────────────────
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not session.get('cart'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        order_details = {
            'name':           request.form.get('name'),
            'email':          request.form.get('email'),
            'phone':          request.form.get('phone'),
            'address':        request.form.get('address'),
            'payment_method': request.form.get('payment_method'),
        }
        session.pop('cart', None)
        return render_template('order_success.html', order=order_details)

    return render_template('checkout.html')


# ── Buy Now ───────────────────────────────────────────────────────
@app.route('/buy_now_direct', methods=['POST'])
def buy_now_direct():
    name = request.form.get('buy_now_item')
    if name:
        if 'cart' not in session:
            session['cart'] = []
        if name not in session['cart']:
            session['cart'].append(name)
            session.modified = True
    return redirect(url_for('checkout'))


# ── Clear Cart ────────────────────────────────────────────────────
@app.route('/clear-cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('index'))

# ── About ──────────────────────────────────────────────────────────
@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
