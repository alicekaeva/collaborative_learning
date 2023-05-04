<?php

namespace App\Repository;

use App\Entity\Group;
use App\Entity\Message;
use App\Entity\User;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<Message>
 *
 * @method Message|null find($id, $lockMode = null, $lockVersion = null)
 * @method Message|null findOneBy(array $criteria, array $orderBy = null)
 * @method Message[]    findAll()
 * @method Message[]    findBy(array $criteria, array $orderBy = null, $limit = null, $offset = null)
 */
class MessageRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Message::class);
    }

    public function save(Message $entity, bool $flush = false): void
    {
        $this->getEntityManager()->persist($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function remove(Message $entity, bool $flush = false): void
    {
        $this->getEntityManager()->remove($entity);

        if ($flush) {
            $this->getEntityManager()->flush();
        }
    }

    public function findAllUsersDialogs(int|User $user): array
    {
        return $this->createQueryBuilder('m')
            ->select('DISTINCT u.fullName, u.id, MAX(m.sendingDate) AS lastSentDate')
            ->leftJoin(User::class, 'u', 'WITH', 'u.id = m.sender OR u.id = m.receiver')
            ->where('m.sender = :user OR m.receiver = :user')
            ->andWhere('u.id <> :user')
            ->groupBy('u.id')
            ->orderBy('lastSentDate', 'DESC')
            ->setParameter('user', $user instanceof User ? $user->getId() : $user)
            ->getQuery()
            ->getResult();
    }

    public function findFullDialog(int|User $first, int|User $second): array
    {
        return $this->createQueryBuilder('m')
            ->Where('m.sender = :first OR m.receiver = :first')
            ->andWhere('m.sender = :second OR m.receiver = :second')
            ->setParameter('first',
                $first instanceof User ? $first->getId() : $first)
            ->setParameter('second',
                $second instanceof User ? $second->getId() : $second)
            ->getQuery()
            ->getResult();
    }

    public function findGroupChat(int|Group $receivingGroup): array
    {
        return $this->createQueryBuilder('m')
            ->where('m.receivingGroup = :receivingGroup')
            ->setParameter('receivingGroup',
                $receivingGroup instanceof Group ? $receivingGroup->getId() : $receivingGroup)
            ->getQuery()
            ->getResult();
    }
}
