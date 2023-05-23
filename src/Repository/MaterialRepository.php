<?php

namespace App\Repository;

use App\Entity\Category;
use App\Entity\Material;
use App\Entity\Tag;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<Material>
 *
 * @method Material|null find($id, $lockMode = null, $lockVersion = null)
 * @method Material|null findOneBy(array $criteria, array $orderBy = null)
 * @method Material[]    findAll()
 * @method Material[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class MaterialRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Material::class);
    }

    public function save(Material $entity, bool $flush = false): void
    {
        $this->getEntityManager()->persist($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function remove(Material $entity, bool $flush = false): void
    {
        $this->getEntityManager()->remove($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function findRecommendedMaterials(array $tags): array
    {
        return $this->createQueryBuilder('m')
            ->join('m.creatorGroup', 'g')
            ->join('g.tags', 't')
            ->where('m.isPrivate = false')
            ->andWhere('t IN (:tags)')
            ->setParameter('tags', $tags)
            ->getQuery()
            ->getResult();
    }

    public function findMaterialsByTag(Tag $tag): array
    {
        return $this->createQueryBuilder('m')
            ->join('m.creatorGroup', 'g')
            ->join('g.tags', 't')
            ->where('m.isPrivate = false')
            ->andWhere(':tag MEMBER OF g.tags')
            ->setParameter('tag', $tag)
            ->getQuery()
            ->getResult();
    }

    public function findMaterialsByCategory(Category $category): array
    {
        return $this->createQueryBuilder('m')
            ->join('m.creatorGroup', 'g')
            ->join('g.tags', 't')
            ->join('t.category', 'c')
            ->where('m.isPrivate = false')
            ->andWhere('c.id = :category_id')
            ->setParameter('category_id', $category->getId())
            ->getQuery()
            ->getResult();
    }
}
