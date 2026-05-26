document.addEventListener("DOMContentLoaded", function () {

    // Show variants
    document.querySelectorAll(".show-variants").forEach(button => {

        button.addEventListener("click", function () {

            let itemId = this.dataset.item;

            let box = document.getElementById(`variants-${itemId}`);

            box.classList.toggle("d-none");

        });

    });


    // Add to cart
    document.querySelectorAll(".add-to-cart").forEach(button => {

        button.addEventListener("click", function () {

            let id = this.dataset.id;

            fetch(`/add-to-cart/${id}/`)
            .then(response => response.json())
            .then(data => {

                if (data.login_required) {
                    window.location.href = "/login/";
                    return;
                }

                if (data.success) {

                    let bubble = document.getElementById("cart-count");

                    if (bubble) {
                        bubble.innerText = data.cart_count;

                        if (data.cart_count > 0) {
                            bubble.style.display = "inline";
                        } else {
                            bubble.style.display = "none";
                        }
                    }

                }

            });

        });

    });

});