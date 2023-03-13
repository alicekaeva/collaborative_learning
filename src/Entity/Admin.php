<?php

namespace App\Entity;

use App\Repository\AdminRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: AdminRepository::class)]
#[ORM\Table(name: '`admin`')]
class Admin
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\OneToOne(cascade: ['persist', 'remove'])]
    #[ORM\JoinColumn(nullable: false)]
    private ?User $user = null;

    #[ORM\OneToMany(mappedBy: 'administrator', targetEntity: Group::class)]
    private Collection $managedGroups;

    public function __construct()
    {
        $this->managedGroups = new ArrayCollection();
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
    public function getManagedGroups(): Collection
    {
        return $this->managedGroups;
    }

    public function addManagedGroup(Group $managedGroup): self
    {
        if (!$this->managedGroups->contains($managedGroup)) {
            $this->managedGroups->add($managedGroup);
            $managedGroup->setAdministrator($this);
        }

        return $this;
    }

    public function removeManagedGroup(Group $managedGroup): self
    {
        if ($this->managedGroups->removeElement($managedGroup)) {
            // set the owning side to null (unless already changed)
            if ($managedGroup->getAdministrator() === $this) {
                $managedGroup->setAdministrator(null);
            }
        }

        return $this;
    }
}
