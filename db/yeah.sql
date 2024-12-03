SELECT products.`productName`, cart.`cartQuantity`, products.`price`, cart.`productID` FROM products JOIN cart ON products.`productID` = cart.`productID` WHERE cart.`accountID`=42;
