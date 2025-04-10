-- Update Lakers to Los Angeles Lakers
UPDATE card SET team = 'Los Angeles Lakers' WHERE team = 'Lakers';

-- Update Grizzlies to Memphis Grizzlies
UPDATE card SET team = 'Memphis Grizzlies' WHERE team = 'Grizzlies';

-- Remove non-team values
UPDATE card SET team = NULL WHERE team IN ('Prizm', 'Shipping');

-- Add any other team standardizations as needed 