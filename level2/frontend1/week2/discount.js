let totalShop = parseFloat(prompt(`Input the total value: `));

if (totalShop > 100000){
  let discount = totalShop * 0.7;
  console.log(`The total amount to pay including the discount for this purchase is: ${discount}`);
}
