document.addEventListener("DOMContentLoaded", function () {
    function updateCartTotal() {
        let total = 0;
        document.querySelectorAll("tr[data-product-id]").forEach(row => {
            const price = parseFloat(row.querySelector("td:nth-child(3)").textContent.replace('₹', '')) || 0;
            const quantity = parseInt(row.querySelector(".quantity-input").value) || 0;
            const itemTotalCell = row.querySelector(".item-total");
            const itemTotal = price * quantity;
            itemTotalCell.textContent = "₹" + itemTotal.toFixed(2);
            total += itemTotal;
        });
        const totalElement = document.getElementById("cart-total");
        if (totalElement) {
            totalElement.textContent = total.toFixed(2);
        }
    }

    document.querySelectorAll(".increase-qty, .decrease-qty").forEach(btn => {
        btn.addEventListener("click", function () {
            const row = btn.closest("tr");
            const input = row.querySelector(".quantity-input");
            let qty = parseInt(input.value);
            if (btn.classList.contains("increase-qty")) {
                qty++;
            } else if (btn.classList.contains("decrease-qty") && qty > 1) {
                qty--;
            }
            input.value = qty;
            updateCartTotal();
        });
    });

    document.querySelectorAll(".remove-item").forEach(button => {
        button.addEventListener("click", function () {
            const productId = this.getAttribute("data-product-id");
            const csrfToken = this.getAttribute("data-csrf-token");
            const row = this.closest("tr");

            fetch("/remove-from-cart/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrfToken
                },
                body: `product_id=${productId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    row.remove();
                    updateCartTotal();
                } else {
                    alert("Failed to remove item.");
                }
            });
        });
    });

    updateCartTotal();
});
