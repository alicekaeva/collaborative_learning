<?php

namespace App\Entity;

use App\Repository\TeacherRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: TeacherRepository::class)]
class Teacher
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\OneToOne(cascade: ['persist', 'remove'])]
    #[ORM\JoinColumn(nullable: false)]
    private ?User $user = null;

    #[ORM\ManyToMany(targetEntity: Group::class, mappedBy: 'teachers')]
    private Collection $teachingIn;

    public function __construct()
    {
        $this->teachingIn = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getUser(): ?User
    {
        return $this->user;
    }

    public function setUser(User $user): self
    {
        $this->user = $user;

        return $this;
    }

    /**
     * @return Collection<int, Group>
     */
    public function getTeachingIn(): Collection
    {
        return $this->teachingIn;
    }

    public function addTeachingIn(Group $teachingIn): self
    {
        if (!$this->teachingIn->contains($teachingIn)) {
            $this->teachingIn->add($teachingIn);
            $teachingIn->addTeacher($this);
        }

        return $this;
    }

    public function removeTeachingIn(Group $teachingIn): self
    {
        if ($this->teachingIn->removeElement($teachingIn)) {
            $teachingIn->removeTeacher($this);
        }

        return $this;
    }
}
