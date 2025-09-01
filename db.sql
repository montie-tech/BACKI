CREATE DATABASE recipes_db;

USE recipes_db;

CREATE TABLE recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    ingredients TEXT
);

INSERT INTO recipes (title, description, ingredients) VALUES
('Chicken Tomato Pasta', 'Delicious pasta with chicken and tomato sauce.', 'chicken, tomato, pasta, garlic'),
('Veggie Stir Fry', 'Quick and easy vegetable stir fry.', 'broccoli, carrot, onion, garlic'),
('Chicken Curry', 'Spicy chicken curry with coconut milk.', 'chicken, coconut milk, onion, garlic, tomato');
