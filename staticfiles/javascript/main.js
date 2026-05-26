document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".show-variants").forEach(button => {

    button.addEventListener("click", function () {

        let itemId = this.dataset.item;

        let box = document.getElementById(`variants-${itemId}`);

        box.classList.toggle("d-none");

    });

});

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

                    // update cart bubble
                    let bubble = document.getElementById("cart-count");

                    bubble.innerText = data.cart_count;

                    if (data.cart_count > 0) {
                        bubble.style.display = "inline";
                    } else {
                        bubble.style.display = "none";
                    }

                    // show toast
                    let toast = document.getElementById("toast-box");

                    toast.style.display = "block";

                    setTimeout(() => {
                        toast.style.display = "none";
                    }, 3000);

                }

            });

        });

    });

});
