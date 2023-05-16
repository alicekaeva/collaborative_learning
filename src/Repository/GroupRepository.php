<?php

namespace App\Repository;

use App\Entity\Group;
use App\Entity\Tag;
use App\Entity\User;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<Group>
 *
 * @method Group|null find($id, $lockMode = null, $lockVersion = null)
 * @method Group|null findOneBy(array $criteria, array $orderBy = null)
 * @method Group[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class GroupRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Group::class);
    }

    public function save(Group $entity, bool $flush = false): void
    {
        $this->getEntityManager()->persist($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function remove(Group $entity, bool $flush = false): void
    {
        $this->getEntityManager()->remove($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function findAll(): array
    {
        return $this->createQueryBuilder('g')
            ->addSelect('t', 'c')
            ->join('g.tags', 't')
            ->join('t.category', 'c')
            ->getQuery()
            ->getResult();
    }

    public function findAllGroupsForUser(User $user)
    {
        $qb = $this->createQueryBuilder('g')
            ->leftJoin('g.students', 's')
            ->leftJoin('g.teachers', 't')
            ->leftJoin('g.administrator', 'a')
            ->where('s.user = :user')
            ->orWhere('t.user = :user')
            ->orWhere('a.user = :user')
            ->setParameter('user', $user);

        return $qb->getQuery()->getResult();
    }

    public function findRecommendedGroups(array $tags): array
    {
        return $this->createQueryBuilder('g')
            ->join('g.tags', 't')
            ->where('t IN (:tags)')
            ->setParameter('tags', $tags)
            ->getQuery()
            ->getResult();
    }

    public function findGroupsByTags(Tag $tag): array
    {
        return $this->createQueryBuilder('g')
            ->join('g.tags', 't')
            ->where(':tag MEMBER OF g.tags')
            ->setParameter('tag', $tag)
            ->getQuery()
            ->getResult();
    }
}
