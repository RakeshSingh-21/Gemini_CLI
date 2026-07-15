async function apiCall(url, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong');
    }
    return data;
}

async function register(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const body = Object.fromEntries(formData.entries());
    try {
        await apiCall('/api/register', 'POST', body);
        alert('Registration successful! Please login.');
        window.location.href = '/login';
    } catch (error) {
        alert(error.message);
    }
}

async function login(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const body = Object.fromEntries(formData.entries());
    try {
        const data = await apiCall('/api/login', 'POST', body);
        if (data.role === 'admin') {
            window.location.href = '/admin';
        } else {
            window.location.href = '/';
        }
    } catch (error) {
        alert(error.message);
    }
}

async function logout() {
    await apiCall('/api/logout', 'POST');
    window.location.href = '/login';
}

async function addToCart(productId) {
    try {
        await apiCall('/api/cart/add', 'POST', { product_id: productId, quantity: 1 });
        alert('Added to cart!');
    } catch (error) {
        if (error.message === 'Not logged in') {
            window.location.href = '/login';
        } else {
            alert(error.message);
        }
    }
}

async function removeFromCart(itemId) {
    try {
        await apiCall(`/api/cart/remove/${itemId}`, 'DELETE');
        window.location.reload();
    } catch (error) {
        alert(error.message);
    }
}

async function checkout() {
    try {
        await apiCall('/api/checkout', 'POST');
        alert('Order placed successfully!');
        window.location.href = '/orders';
    } catch (error) {
        alert(error.message);
    }
}

// Admin Functions
async function addProduct(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const body = Object.fromEntries(formData.entries());
    body.price = parseFloat(body.price);
    body.stock = parseInt(body.stock);
    try {
        await apiCall('/api/products', 'POST', body);
        window.location.reload();
    } catch (error) {
        alert(error.message);
    }
}

async function deleteProduct(productId) {
    if (!confirm('Are you sure?')) return;
    try {
        await apiCall(`/api/products/${productId}`, 'DELETE');
        window.location.reload();
    } catch (error) {
        alert(error.message);
    }
}
