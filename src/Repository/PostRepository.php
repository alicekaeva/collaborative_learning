<?php

namespace App\Repository;

use App\Entity\Post;
use App\Entity\User;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<Post>
 *
 * @method Post|null find($id, $lockMode = null, $lockVersion = null)
 * @method Post|null findOneBy(array $criteria, array $orderBy = null)
 * @method Post[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class PostRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Post::class);
    }

    public function save(Post $entity, bool $flush = false): void
    {
        $this->getEntityManager()->persist($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function remove(Post $entity, bool $flush = false): void
    {
        $this->getEntityManager()->remove($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function findAll(): array
    {
        return $this->createQueryBuilder('p')
            ->addSelect('t', 'c')
            ->join('p.tags', 't')
            ->join('t.category', 'c')
            ->orderBy('p.postingDate', 'DESC')
            ->getQuery()
            ->getResult();
    }

    public function findAllByAuthor(int|User $author): array
    {
        return $this->createQueryBuilder('p')
            ->Where('p.author = :author')
            ->setParameter('author',
                $author instanceof User ? $author->getId() : $author)
            ->orderBy('p.postingDate', 'DESC')
            ->getQuery()
            ->getResult();
    }

    public function findRecommendedPosts(array $tags): array
    {
        return $this->createQueryBuilder('p')
            ->join('p.tags', 't')
            ->where('t IN (:tags)')
            ->setParameter('tags', $tags)
            ->getQuery()
            ->getResult();
    }

    public function findFavoritePosts(int|User $user): array
    {
        return $this->createQueryBuilder('p')
            ->join('p.addedToFav', 'f')
            ->where('f = :user')
            ->setParameter('user',
                $user instanceof User ? $user->getId() : $user)
            ->getQuery()
            ->getResult();
    }
}
