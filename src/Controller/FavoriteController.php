<?php

namespace App\Controller;

use App\Entity\Post;
use App\Repository\PostRepository;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;

class FavoriteController extends AbstractController
{
    #[Route('/favorite/{id}', name: 'app_favorite')]
    #[IsGranted('IS_AUTHENTICATED_FULLY')]
    public function favorite(Post $post, PostRepository $posts, Request $request): Response
    {
        $currentUser = $this->getUser();
        $post->addAddedToFav($currentUser);
        $posts->save($post, true);

        return $this->redirect($request->headers->get('referer'));
    }

    #[Route('/unfavorite/{id}', name: 'app_unfavorite')]
    #[IsGranted('IS_AUTHENTICATED_FULLY')]
    public function unfavorite(Post $post, PostRepository $posts, Request $request): Response
    {
        $currentUser = $this->getUser();
        $post->removeAddedToFav($currentUser);
        $posts->save($post, true);

        return $this->redirect($request->headers->get('referer'));
    }
}