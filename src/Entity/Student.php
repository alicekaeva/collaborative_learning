<?php

namespace App\Entity;

use App\Repository\StudentRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: StudentRepository::class)]
class Student
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\OneToOne(cascade: ['persist', 'remove'])]
    #[ORM\JoinColumn(nullable: false)]
    private ?User $user = null;

    #[ORM\ManyToMany(targetEntity: Group::class, mappedBy: 'students')]
    private Collection $studyingIn;

    public function __construct()
    {
        $this->studyingIn = new ArrayCollection();
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
    public function getStudyingIn(): Collection
    {
        return $this->studyingIn;
    }

    public function addStudyingIn(Group $studyingIn): self
    {
        if (!$this->studyingIn->contains($studyingIn)) {
            $this->studyingIn->add($studyingIn);
            $studyingIn->addStudent($this);
        }

        return $this;
    }

    public function removeStudyingIn(Group $studyingIn): self
    {
        if ($this->studyingIn->removeElement($studyingIn)) {
            $studyingIn->removeStudent($this);
        }

        return $this;
    }
}
