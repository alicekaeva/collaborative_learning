<?php

namespace App\Entity;

use App\Repository\PostRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: PostRepository::class)]
class Post
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 500)]
    private ?string $content = null;

    #[ORM\Column(type: Types::DATETIME_IMMUTABLE)]
    private ?\DateTimeImmutable $postingDate = null;

    #[ORM\ManyToOne(inversedBy: 'posts')]
    #[ORM\JoinColumn(nullable: false)]
    private ?User $author = null;

    #[ORM\ManyToMany(targetEntity: User::class, inversedBy: 'favorites')]
    private Collection $addedToFav;

    #[ORM\ManyToMany(targetEntity: Tag::class, inversedBy: 'relatedPosts')]
    private Collection $tags;

    public function __construct()
    {
        $this->addedToFav = new ArrayCollection();
        $this->tags = new ArrayCollection();
        $this->postingDate = new \DateTimeImmutable();
    }

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

    public function getPostingDate(): ?\DateTimeImmutable
    {
        return $this->postingDate;
    }

    public function setPostingDate(\DateTimeImmutable $postingDate): self
    {
        $this->postingDate = $postingDate;

        return $this;
    }

    public function getAuthor(): ?User
    {
        return $this->author;
    }

    public function setAuthor(?User $author): self
    {
        $this->author = $author;

        return $this;
    }

    /**
     * @return Collection<int, User>
     */
    public function getAddedToFav(): Collection
    {
        return $this->addedToFav;
    }

    public function addAddedToFav(User $addedToFav): self
    {
        if (!$this->addedToFav->contains($addedToFav)) {
            $this->addedToFav->add($addedToFav);
        }

        return $this;
    }

    public function removeAddedToFav(User $addedToFav): self
    {
        $this->addedToFav->removeElement($addedToFav);

        return $this;
    }

    /**
     * @return Collection<int, Tag>
     */
    public function getTags(): Collection
    {
        return $this->tags;
    }

    public function addTag(Tag $tag): self
    {
        if (!$this->tags->contains($tag)) {
            $this->tags->add($tag);
        }

        return $this;
    }

    public function removeTag(Tag $tag): self
    {
        $this->tags->removeElement($tag);

        return $this;
    }
}
