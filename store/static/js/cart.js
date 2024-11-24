// JavaScript to handle "Add to Cart" on clicking the product card
document.addEventListener('DOMContentLoaded', function () {
    const productCards = document.querySelectorAll('.product-card'); // Select product cards

    productCards.forEach(card => {
        card.addEventListener('click', function (event) {
            // Prevent any link or other default behavior
            event.preventDefault();

            // Get the product ID from the clicked card
            const productId = card.getAttribute('data-product');
            
            // Send POST request to add item to cart
            fetch('/add-to-cart/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    'product_id': productId,
                    'action': 'add'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the cart count in the navbar
                    const cartCount = document.getElementById('cart-count');
                    cartCount.textContent = data.cart_count; // Set the new cart count
                    
                    // Optionally, show a success message or notification
                    alert('Product added to cart!');
                } else {
                    alert('Error adding item to cart');
                }
            })
            .catch(error => console.log('Error:', error));
        });
    });
});
