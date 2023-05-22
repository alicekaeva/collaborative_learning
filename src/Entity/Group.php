<?php

namespace App\Entity;

use App\Repository\GroupRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: GroupRepository::class)]
#[ORM\Table(name: '`group`')]
class Group
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 255)]
    private ?string $name = null;

    #[ORM\Column(length: 500)]
    private ?string $info = null;

    #[ORM\ManyToOne(inversedBy: 'managedGroups')]
    #[ORM\JoinColumn(nullable: false)]
    private ?Admin $administrator = null;

    #[ORM\ManyToMany(targetEntity: Teacher::class, inversedBy: 'teachingIn')]
    private Collection $teachers;

    #[ORM\ManyToMany(targetEntity: Student::class, inversedBy: 'studyingIn')]
    private Collection $students;

    #[ORM\ManyToMany(targetEntity: Tag::class, inversedBy: 'relatedGroups')]
    private Collection $tags;

    #[ORM\OneToMany(mappedBy: 'creator', targetEntity: Goal::class, orphanRemoval: true)]
    private Collection $goals;

    #[ORM\OneToMany(mappedBy: 'creator', targetEntity: Task::class, orphanRemoval: true)]
    private Collection $tasks;

    #[ORM\OneToMany(mappedBy: 'creator', targetEntity: Meeting::class, orphanRemoval: true)]
    private Collection $meetings;

    #[ORM\OneToMany(mappedBy: 'creatorGroup', targetEntity: Material::class)]
    private Collection $materials;

    #[ORM\OneToMany(mappedBy: 'receivingGroup', targetEntity: Message::class, orphanRemoval: true)]
    private Collection $messages;

    #[ORM\Column]
    private ?int $requiredTeachers = null;

    #[ORM\Column]
    private ?int $requiredStudents = null;

    public function __construct()
    {
        $this->teachers = new ArrayCollection();
        $this->students = new ArrayCollection();
        $this->tags = new ArrayCollection();
        $this->goals = new ArrayCollection();
        $this->tasks = new ArrayCollection();
        $this->meetings = new ArrayCollection();
        $this->materials = new ArrayCollection();
        $this->messages = new ArrayCollection();
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

    public function getInfo(): ?string
    {
        return $this->info;
    }

    public function setInfo(string $info): self
    {
        $this->info = $info;

        return $this;
    }

    public function getAdministrator(): ?Admin
    {
        return $this->administrator;
    }

    public function setAdministrator(?Admin $administrator): self
    {
        $this->administrator = $administrator;

        return $this;
    }

    /**
     * @return Collection<int, Teacher>
     */
    public function getTeachers(): Collection
    {
        return $this->teachers;
    }

    public function addTeacher(Teacher $teacher): self
    {
        if (!$this->teachers->contains($teacher)) {
            $this->teachers->add($teacher);
        }

        return $this;
    }

    public function removeTeacher(Teacher $teacher): self
    {
        $this->teachers->removeElement($teacher);

        return $this;
    }

    /**
     * @return Collection<int, Student>
     */
    public function getStudents(): Collection
    {
        return $this->students;
    }

    public function addStudent(Student $student): self
    {
        if (!$this->students->contains($student)) {
            $this->students->add($student);
        }

        return $this;
    }

    public function removeStudent(Student $student): self
    {
        $this->students->removeElement($student);

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

    /**
     * @return Collection<int, Goal>
     */
    public function getGoals(): Collection
    {
        return $this->goals;
    }

    public function addGoal(Goal $goal): self
    {
        if (!$this->goals->contains($goal)) {
            $this->goals->add($goal);
            $goal->setCreator($this);
        }

        return $this;
    }

    public function removeGoal(Goal $goal): self
    {
        if ($this->goals->removeElement($goal)) {
            // set the owning side to null (unless already changed)
            if ($goal->getCreator() === $this) {
                $goal->setCreator(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Task>
     */
    public function getTasks(): Collection
    {
        return $this->tasks;
    }

    public function addTask(Task $task): self
    {
        if (!$this->tasks->contains($task)) {
            $this->tasks->add($task);
            $task->setCreator($this);
        }

        return $this;
    }

    public function removeTask(Task $task): self
    {
        if ($this->tasks->removeElement($task)) {
            // set the owning side to null (unless already changed)
            if ($task->getCreator() === $this) {
                $task->setCreator(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Meeting>
     */
    public function getMeetings(): Collection
    {
        return $this->meetings;
    }

    public function addMeeting(Meeting $meeting): self
    {
        if (!$this->meetings->contains($meeting)) {
            $this->meetings->add($meeting);
            $meeting->setCreator($this);
        }

        return $this;
    }

    public function removeMeeting(Meeting $meeting): self
    {
        if ($this->meetings->removeElement($meeting)) {
            // set the owning side to null (unless already changed)
            if ($meeting->getCreator() === $this) {
                $meeting->setCreator(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Material>
     */
    public function getMaterials(): Collection
    {
        return $this->materials;
    }

    public function addMaterial(Material $material): self
    {
        if (!$this->materials->contains($material)) {
            $this->materials->add($material);
            $material->setCreatorGroup($this);
        }

        return $this;
    }

    public function removeMaterial(Material $material): self
    {
        if ($this->materials->removeElement($material)) {
            // set the owning side to null (unless already changed)
            if ($material->getCreatorGroup() === $this) {
                $material->setCreatorGroup(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Message>
     */
    public function getMessages(): Collection
    {
        return $this->messages;
    }

    public function addMessage(Message $message): self
    {
        if (!$this->messages->contains($message)) {
            $this->messages->add($message);
            $message->setReceivingGroup($this);
        }

        return $this;
    }

    public function removeMessage(Message $message): self
    {
        if ($this->messages->removeElement($message)) {
            // set the owning side to null (unless already changed)
            if ($message->getReceivingGroup() === $this) {
                $message->setReceivingGroup(null);
            }
        }

        return $this;
    }

    public function getRequiredTeachers(): ?int
    {
        return $this->requiredTeachers;
    }

    public function setRequiredTeachers(int $requiredTeachers): self
    {
        $this->requiredTeachers = $requiredTeachers;

        return $this;
    }

    public function getRequiredStudents(): ?int
    {
        return $this->requiredStudents;
    }

    public function setRequiredStudents(int $requiredStudents): self
    {
        $this->requiredStudents = $requiredStudents;

        return $this;
    }

    public function __toString()
    {
        return $this->getName();
    }
}
