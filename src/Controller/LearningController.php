<?php

namespace App\Controller;

use App\Entity\Group;
use App\Entity\Message;
use App\Entity\User;
use App\Repository\GroupRepository;
use App\Repository\MessageRepository;
use App\Repository\UserRepository;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\HttpFoundation\Cookie;

#[Route('/learning')]
#[IsGranted('IS_AUTHENTICATED_FULLY')]
class LearningController extends AbstractController
{
    #[Route('/', name: 'app_learning_index', methods: ['GET'])]
    public function index(GroupRepository $groupRepository): Response
    {
        $user = $this->getUser();
        $groups = $groupRepository->findAllGroupsForUser($user);

        return $this->render('learning/index.html.twig', [
            'groups' => $groups,
            'activeGroup' => null,
        ]);
    }

    #[Route('/group/{id}', name: 'app_learning_show', methods: ['GET'])]
    public function show(MessageRepository $messageRepository, GroupRepository $groupRepository, Group $receivingGroup, UserRepository $userRepository): Response
    {
        /** @var User $user */
        $user = $this->getUser();
        $groups = $groupRepository->findAllGroupsForUser($user);
        $chat = $messageRepository->findGroupChat($receivingGroup);

        $cookie = Cookie::create('currentGroup')
            ->withValue($receivingGroup->getId())
            ->withExpires(new \DateTime('+1 day'))
            ->withSecure(true)
            ->withHttpOnly(true);

        $response = $this->render('learning/index.html.twig', [
            'groups' => $groups,
            'activeGroup' => $receivingGroup,
            'chat' => $chat,
            'users' => $userRepository->findAll()
        ]);
        $response->headers->setCookie($cookie);

        return $response;
    }

    #[Route('/send', name: 'app_learning_send', methods: ['POST'])]
    public function send(Request $request, MessageRepository $messageRepository, GroupRepository $groupRepository): Response
    {
        $user = $this->getUser();
        $receiverId = $request->request->get('receiver_id');
        $receiver = $groupRepository->findOneBy(['id' => $receiverId]);
        $content = $request->request->get('content');

        $message = new Message();
        $message->setSender($user);
        $message->setReceivingGroup($receiver);
        $message->setContent($content);
        $message->setSendingDate(new \DateTimeImmutable());
        $messageRepository->save($message, true);

        return $this->redirectToRoute('app_learning_show', ['id' => $receiverId]);
    }
}