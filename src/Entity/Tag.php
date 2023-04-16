<?php

namespace App\Entity;

use App\Repository\TagRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: TagRepository::class)]
class Tag
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 255)]
    private ?string $name = null;

    #[ORM\ManyToOne(inversedBy: 'tags')]
    #[ORM\JoinColumn(nullable: false)]
    private ?Category $category = null;

    #[ORM\ManyToMany(targetEntity: User::class, inversedBy: 'tags')]
    private Collection $users;

    #[ORM\ManyToMany(targetEntity: Post::class, mappedBy: 'tags')]
    private Collection $relatedPosts;

    #[ORM\ManyToMany(targetEntity: Group::class, mappedBy: 'tags')]
    private Collection $relatedGroups;

    public function __construct()
    {
        $this->users = new ArrayCollection();
        $this->relatedPosts = new ArrayCollection();
        $this->relatedGroups = new ArrayCollection();
    }

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

    public function getCategory(): ?Category
    {
        return $this->category;
    }

    public function setCategory(?Category $category): self
    {
        $this->category = $category;

        return $this;
    }

    /**
     * @return Collection<int, User>
     */
    public function getUsers(): Collection
    {
        return $this->users;
    }

    public function addUser(User $user): self
    {
        if (!$this->users->contains($user)) {
            $this->users->add($user);
        }

        return $this;
    }

    public function removeUser(User $user): self
    {
        $this->users->removeElement($user);

        return $this;
    }

    /**
     * @return Collection<int, Post>
     */
    public function getRelatedPosts(): Collection
    {
        return $this->relatedPosts;
    }

    public function addRelatedPost(Post $relatedPost): self
    {
        if (!$this->relatedPosts->contains($relatedPost)) {
            $this->relatedPosts->add($relatedPost);
            $relatedPost->addTag($this);
        }

        return $this;
    }

    public function removeRelatedPost(Post $relatedPost): self
    {
        if ($this->relatedPosts->removeElement($relatedPost)) {
            $relatedPost->removeTag($this);
        }

        return $this;
    }

    /**
     * @return Collection<int, Group>
     */
    public function getRelatedGroups(): Collection
    {
        return $this->relatedGroups;
    }

    public function addRelatedGroup(Group $relatedGroup): self
    {
        if (!$this->relatedGroups->contains($relatedGroup)) {
            $this->relatedGroups->add($relatedGroup);
            $relatedGroup->addTag($this);
        }

        return $this;
    }

    public function removeRelatedGroup(Group $relatedGroup): self
    {
        if ($this->relatedGroups->removeElement($relatedGroup)) {
            $relatedGroup->removeTag($this);
        }

        return $this;
    }

    public function __toString()
    {
        return $this->getName() . PHP_EOL;
    }
}
