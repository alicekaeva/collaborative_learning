<?php

namespace App\Entity;

use App\Repository\MeetingRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: MeetingRepository::class)]
class Meeting
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 255)]
    private ?string $name = null;

    #[ORM\Column(length: 500, nullable: true)]
    private ?string $agenda = null;

    #[ORM\Column(length: 255, nullable: true)]
    private ?string $link = null;

    #[ORM\Column(type: Types::DATETIME_IMMUTABLE)]
    private ?\DateTimeImmutable $heldOn = null;

    #[ORM\ManyToOne(inversedBy: 'meetings')]
    #[ORM\JoinColumn(nullable: false)]
    private ?Group $creator = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getName(): ?string
    {
        return $this->name;
    }

    public function setName(string $name): self
    {
        $this->name = $name;

        return $this;
    }

    public function getAgenda(): ?string
    {
        return $this->agenda;
    }

    public function setAgenda(?string $agenda): self
    {
        $this->agenda = $agenda;

        return $this;
    }

    public function getLink(): ?string
    {
        return $this->link;
    }

    public function setLink(?string $link): self
    {
        $this->link = $link;

        return $this;
    }

    public function getHeldOn(): ?\DateTimeImmutable
    {
        return $this->heldOn;
    }

    public function setHeldOn(\DateTimeImmutable $heldOn): self
    {
        $this->heldOn = $heldOn;

        return $this;
    }

    public function getCreator(): ?Group
    {
        return $this->creator;
    }

    public function setCreator(?Group $creator): self
    {
        $this->creator = $creator;

        return $this;
    }
}
