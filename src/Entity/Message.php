<?php

namespace App\Entity;

use App\Repository\MessageRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: MessageRepository::class)]
class Message
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 1000)]
    private ?string $content = null;

    #[ORM\Column(nullable: true)]
    private ?bool $isPinned = null;

    #[ORM\Column(type: Types::DATETIME_IMMUTABLE)]
    private ?\DateTimeImmutable $sendingDate = null;

    #[ORM\ManyToOne(inversedBy: 'messages')]
    #[ORM\JoinColumn(nullable: false)]
    private ?User $sender = null;

    #[ORM\ManyToOne(inversedBy: 'messages')]
    private ?User $receiver = null;

    #[ORM\ManyToOne(inversedBy: 'messages')]
    private ?Group $receivingGroup = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getContent(): ?string
    {
        return $this->content;
    }

    public function setContent(string $content): self
    {
        $this->content = $content;

        return $this;
    }

    public function isIsPinned(): ?bool
    {
        return $this->isPinned;
    }

    public function setIsPinned(bool $isPinned): self
    {
        $this->isPinned = $isPinned;

        return $this;
    }

    public function getSendingDate(): ?\DateTimeImmutable
    {
        return $this->sendingDate;
    }

    public function setSendingDate(\DateTimeImmutable $sendingDate): self
    {
        $this->sendingDate = $sendingDate;

        return $this;
    }

    public function getSender(): ?User
    {
        return $this->sender;
    }

    public function setSender(?User $sender): self
    {
        $this->sender = $sender;

        return $this;
    }

    public function getReceiver(): ?User
    {
        return $this->receiver;
    }

    public function setReceiver(?User $receiver): self
    {
        $this->receiver = $receiver;

        return $this;
    }

    public function getReceivingGroup(): ?Group
    {
        return $this->receivingGroup;
    }

    public function setReceivingGroup(?Group $receivingGroup): self
    {
        $this->receivingGroup = $receivingGroup;

        return $this;
    }
}
