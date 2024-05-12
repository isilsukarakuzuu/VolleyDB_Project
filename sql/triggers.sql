DELIMITER //

CREATE TRIGGER check_username_unique_coach
BEFORE INSERT ON Coach
FOR EACH ROW
BEGIN
    DECLARE username_count INT;

    -- Check in the Jury table
    SELECT COUNT(*) INTO username_count FROM Jury WHERE username = NEW.username;
    IF username_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists in Jury table';
    END IF;

    -- Check in the Player table
    SELECT COUNT(*) INTO username_count FROM Player WHERE username = NEW.username;
    IF username_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists in Player table';
    END IF;

    -- Check in the DatabaseManager table
    SELECT COUNT(*) INTO username_count FROM DatabaseManager WHERE username = NEW.username;
    IF username_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists in DatabaseManager table';
    END IF;
END//

CREATE TRIGGER check_username_unique_jury
BEFORE INSERT ON Jury
FOR EACH ROW
BEGIN
    DECLARE username_count INT;

    -- Check in the Coach table
    SELECT COUNT(*) INTO username_count FROM Coach WHERE username = NEW.username;
    IF username_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists in Coach table';
    END IF;

    -- Check in the Player table
    SELECT COUNT(*) INTO username_count FROM Player WHERE username = NEW.username;
    IF username_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists in Player table';
    END IF;

    -- Check in the DatabaseManager table
    SELECT COUNT(*) INTO username_count FROM DatabaseManager WHERE username = NEW.username;
    IF username_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists in DatabaseManager table';
    END IF;
END//

CREATE TRIGGER check_username_unique_player
BEFORE INSERT ON Player
FOR EACH ROW
BEGIN
    DECLARE username_count INT;

    -- Check in the Coach table
    SELECT COUNT(*) INTO username_count FROM Coach WHERE username = NEW.username;
    IF username_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists in Coach table';
    END IF;

    -- Check in the Jury table
    SELECT COUNT(*) INTO username_count FROM Jury WHERE username = NEW.username;
    IF username_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists in Jury table';
    END IF;

    -- Check in the DatabaseManager table
    SELECT COUNT(*) INTO username_count FROM DatabaseManager WHERE username = NEW.username;
    IF username_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Username already exists in DatabaseManager table';
    END IF;
END//

CREATE TRIGGER prevent_additional_db_manager
BEFORE INSERT ON DatabaseManager
FOR EACH ROW
BEGIN
    -- Signal an error to prevent insertion
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Adding new Database Managers is not allowed';
END//

DELIMITER ;
