<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20230313011529 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE goal (id INT AUTO_INCREMENT NOT NULL, creator_id INT NOT NULL, name VARCHAR(255) NOT NULL, points INT DEFAULT NULL, deadline DATETIME DEFAULT NULL, INDEX IDX_FCDCEB2E61220EA6 (creator_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE `group` (id INT AUTO_INCREMENT NOT NULL, administrator_id INT NOT NULL, name VARCHAR(255) NOT NULL, info VARCHAR(500) NOT NULL, INDEX IDX_6DC044C54B09E92C (administrator_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE group_teacher (group_id INT NOT NULL, teacher_id INT NOT NULL, INDEX IDX_36F6F2D9FE54D947 (group_id), INDEX IDX_36F6F2D941807E1D (teacher_id), PRIMARY KEY(group_id, teacher_id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE group_student (group_id INT NOT NULL, student_id INT NOT NULL, INDEX IDX_3123FB3FFE54D947 (group_id), INDEX IDX_3123FB3FCB944F1A (student_id), PRIMARY KEY(group_id, student_id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE group_tag (group_id INT NOT NULL, tag_id INT NOT NULL, INDEX IDX_801B5FFAFE54D947 (group_id), INDEX IDX_801B5FFABAD26311 (tag_id), PRIMARY KEY(group_id, tag_id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE material (id INT AUTO_INCREMENT NOT NULL, creator_group_id INT NOT NULL, creator_user_id INT NOT NULL, name VARCHAR(255) NOT NULL, file_link VARCHAR(255) NOT NULL, mime_type VARCHAR(255) NOT NULL, is_private TINYINT(1) NOT NULL, INDEX IDX_7CBE7595A9B2FEDB (creator_group_id), INDEX IDX_7CBE759529FC6AE1 (creator_user_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE media (id INT AUTO_INCREMENT NOT NULL, link_to_file VARCHAR(255) NOT NULL, mime_type VARCHAR(255) NOT NULL, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE meeting (id INT AUTO_INCREMENT NOT NULL, creator_id INT NOT NULL, name VARCHAR(255) NOT NULL, agenda VARCHAR(500) DEFAULT NULL, link VARCHAR(255) DEFAULT NULL, held_on DATETIME NOT NULL, INDEX IDX_F515E13961220EA6 (creator_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE message (id INT AUTO_INCREMENT NOT NULL, sender_id INT NOT NULL, receiver_id INT DEFAULT NULL, receiving_group_id INT DEFAULT NULL, content VARCHAR(1000) NOT NULL, is_pinned TINYINT(1) NOT NULL, sending_date DATETIME NOT NULL, INDEX IDX_B6BD307FF624B39D (sender_id), INDEX IDX_B6BD307FCD53EDB6 (receiver_id), INDEX IDX_B6BD307FC7B9E60E (receiving_group_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('CREATE TABLE task (id INT AUTO_INCREMENT NOT NULL, creator_id INT NOT NULL, name VARCHAR(255) NOT NULL, link VARCHAR(255) DEFAULT NULL, deadline DATETIME DEFAULT NULL, points INT DEFAULT NULL, INDEX IDX_527EDB2561220EA6 (creator_id), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('ALTER TABLE goal ADD CONSTRAINT FK_FCDCEB2E61220EA6 FOREIGN KEY (creator_id) REFERENCES `group` (id)');
        $this->addSql('ALTER TABLE `group` ADD CONSTRAINT FK_6DC044C54B09E92C FOREIGN KEY (administrator_id) REFERENCES `admin` (id)');
        $this->addSql('ALTER TABLE group_teacher ADD CONSTRAINT FK_36F6F2D9FE54D947 FOREIGN KEY (group_id) REFERENCES `group` (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE group_teacher ADD CONSTRAINT FK_36F6F2D941807E1D FOREIGN KEY (teacher_id) REFERENCES teacher (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE group_student ADD CONSTRAINT FK_3123FB3FFE54D947 FOREIGN KEY (group_id) REFERENCES `group` (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE group_student ADD CONSTRAINT FK_3123FB3FCB944F1A FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE group_tag ADD CONSTRAINT FK_801B5FFAFE54D947 FOREIGN KEY (group_id) REFERENCES `group` (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE group_tag ADD CONSTRAINT FK_801B5FFABAD26311 FOREIGN KEY (tag_id) REFERENCES tag (id) ON DELETE CASCADE');
        $this->addSql('ALTER TABLE material ADD CONSTRAINT FK_7CBE7595A9B2FEDB FOREIGN KEY (creator_group_id) REFERENCES `group` (id)');
        $this->addSql('ALTER TABLE material ADD CONSTRAINT FK_7CBE759529FC6AE1 FOREIGN KEY (creator_user_id) REFERENCES user (id)');
        $this->addSql('ALTER TABLE meeting ADD CONSTRAINT FK_F515E13961220EA6 FOREIGN KEY (creator_id) REFERENCES `group` (id)');
        $this->addSql('ALTER TABLE message ADD CONSTRAINT FK_B6BD307FF624B39D FOREIGN KEY (sender_id) REFERENCES user (id)');
        $this->addSql('ALTER TABLE message ADD CONSTRAINT FK_B6BD307FCD53EDB6 FOREIGN KEY (receiver_id) REFERENCES user (id)');
        $this->addSql('ALTER TABLE message ADD CONSTRAINT FK_B6BD307FC7B9E60E FOREIGN KEY (receiving_group_id) REFERENCES `group` (id)');
        $this->addSql('ALTER TABLE task ADD CONSTRAINT FK_527EDB2561220EA6 FOREIGN KEY (creator_id) REFERENCES `group` (id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('ALTER TABLE goal DROP FOREIGN KEY FK_FCDCEB2E61220EA6');
        $this->addSql('ALTER TABLE `group` DROP FOREIGN KEY FK_6DC044C54B09E92C');
        $this->addSql('ALTER TABLE group_teacher DROP FOREIGN KEY FK_36F6F2D9FE54D947');
        $this->addSql('ALTER TABLE group_teacher DROP FOREIGN KEY FK_36F6F2D941807E1D');
        $this->addSql('ALTER TABLE group_student DROP FOREIGN KEY FK_3123FB3FFE54D947');
        $this->addSql('ALTER TABLE group_student DROP FOREIGN KEY FK_3123FB3FCB944F1A');
        $this->addSql('ALTER TABLE group_tag DROP FOREIGN KEY FK_801B5FFAFE54D947');
        $this->addSql('ALTER TABLE group_tag DROP FOREIGN KEY FK_801B5FFABAD26311');
        $this->addSql('ALTER TABLE material DROP FOREIGN KEY FK_7CBE7595A9B2FEDB');
        $this->addSql('ALTER TABLE material DROP FOREIGN KEY FK_7CBE759529FC6AE1');
        $this->addSql('ALTER TABLE meeting DROP FOREIGN KEY FK_F515E13961220EA6');
        $this->addSql('ALTER TABLE message DROP FOREIGN KEY FK_B6BD307FF624B39D');
        $this->addSql('ALTER TABLE message DROP FOREIGN KEY FK_B6BD307FCD53EDB6');
        $this->addSql('ALTER TABLE message DROP FOREIGN KEY FK_B6BD307FC7B9E60E');
        $this->addSql('ALTER TABLE task DROP FOREIGN KEY FK_527EDB2561220EA6');
        $this->addSql('DROP TABLE goal');
        $this->addSql('DROP TABLE `group`');
        $this->addSql('DROP TABLE group_teacher');
        $this->addSql('DROP TABLE group_student');
        $this->addSql('DROP TABLE group_tag');
        $this->addSql('DROP TABLE material');
        $this->addSql('DROP TABLE media');
        $this->addSql('DROP TABLE meeting');
        $this->addSql('DROP TABLE message');
        $this->addSql('DROP TABLE task');
    }
}
