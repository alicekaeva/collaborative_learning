<?php

namespace App\Controller;

use App\Entity\Message;
use App\Entity\User;
use App\Form\MessageType;
use App\Repository\MessageRepository;
use App\Repository\UserRepository;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

#[Route('/message')]
#[IsGranted('IS_AUTHENTICATED_FULLY')]
class MessageController extends AbstractController
{
    #[Route('/', name: 'app_message_index', methods: ['GET'])]
    public function index(MessageRepository $messageRepository): Response
    {
        /** @var User $user */
        $user = $this->getUser();
        $dialogs = $messageRepository->findAllUsersDialogs($user);

        return $this->render('message/index.html.twig', [
            'dialogs' => $dialogs,
            'activeUser' => null,
        ]);
    }

    #[Route('/new', name: 'app_message_new', methods: ['GET', 'POST'])]
    public function new(Request $request, MessageRepository $messageRepository): Response
    {
        $message = new Message();
        $form = $this->createForm(MessageType::class, $message);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $messageRepository->save($message, true);

            return $this->redirectToRoute('app_message_index', [], Response::HTTP_SEE_OTHER);
        }

        return $this->renderForm('message/new.html.twig', [
            'message' => $message,
            'form' => $form,
        ]);
    }

    #[Route('/send', name: 'app_message_send', methods: ['POST'])]
    public function send(Request $request, MessageRepository $messageRepository, UserRepository $userRepository): Response
    {
        $user = $this->getUser();
        $receiverId = $request->request->get('receiver_id');
        $receiver = $userRepository->findOneBy(['id'=>$receiverId]);
        $content = $request->request->get('content');

        $message = new Message();
        $message->setSender($user);
        $message->setReceiver($receiver);
        $message->setContent($content);
        $message->setSendingDate(new \DateTimeImmutable());
        $messageRepository->save($message, true);

        return $this->redirectToRoute('app_message_show', ['id' => $receiverId]);
    }

    #[Route('/pin/{id}', name: 'app_pin')]
    public function pin(Message $message, MessageRepository $messageRepository, Request $request): Response
    {
        $message->setIsPinned(true);
        $messageRepository->save($message, true);

        return $this->redirect($request->headers->get('referer'));
    }

    #[Route('/unpin/{id}', name: 'app_unpin')]
    public function unpin(Message $message, MessageRepository $messageRepository, Request $request): Response
    {
        $message->setIsPinned(false);
        $messageRepository->save($message, true);

        return $this->redirect($request->headers->get('referer'));
    }

    #[Route('/dialog/{id}', name: 'app_message_show', methods: ['GET'])]
    public function show(MessageRepository $messageRepository, User $receiver): Response
    {
        /** @var User $user */
        $user = $this->getUser();
        $dialogs = $messageRepository->findAllUsersDialogs($user);

        $chat = $messageRepository->findFullDialog($user, $receiver);

        return $this->render('message/index.html.twig', [
            'dialogs' => $dialogs,
            'activeUser' => $receiver,
            'chat' => $chat,
        ]);
    }

    #[Route('/{id}/edit', name: 'app_message_edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, Message $message, MessageRepository $messageRepository): Response
    {
        $form = $this->createForm(MessageType::class, $message);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $messageRepository->save($message, true);

            return $this->redirectToRoute('app_message_index', [], Response::HTTP_SEE_OTHER);
        }

        return $this->renderForm('message/edit.html.twig', [
            'message' => $message,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_message_delete', methods: ['POST'])]
    public function delete(Request $request, Message $message, MessageRepository $messageRepository): Response
    {
        if ($this->isCsrfTokenValid('delete' . $message->getId(), $request->request->get('_token'))) {
            $messageRepository->remove($message, true);
        }

        return $this->redirectToRoute('app_message_index', [], Response::HTTP_SEE_OTHER);
    }
}
