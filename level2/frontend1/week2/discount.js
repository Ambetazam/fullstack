let totalShop = parseFloat(prompt(`Input the total value: `));

if (totalShop > 100000 && ){
  let discount = totalShop * 0.7;
  console.log(`The total amount to pay including the discount for this purchase is: ${discount}`);
  alert(`Thank you for your purchase you need to pay: $ ${discount} usd`)
} else {
  if (totalShop >= 50000 <= 60000){
    let discount_two = totalShop * 0.4;
    console.log(`The amount to pay is: ${discount_two}`);
    alert(`Thank you for your purchase, the amount to pay is: ${discount_two} usd`)

  }
}

