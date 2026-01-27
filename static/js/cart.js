function updateQty(productId, change) {
    fetch(`/update-cart/${productId}/${change}`)
      .then(() => location.reload());
  }
  