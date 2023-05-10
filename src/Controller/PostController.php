<?php

namespace App\Controller;

use App\Entity\Post;
use App\Entity\User;
use App\Form\PostType;
use App\Repository\CategoryRepository;
use App\Repository\PostRepository;
use App\Repository\TagRepository;
use Sensio\Bundle\FrameworkExtraBundle\Configuration\IsGranted;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

#[Route('/post')]
class PostController extends AbstractController
{
    #[Route('/', name: 'app_post_index', methods: ['GET'])]
    public function index(PostRepository $postRepository): Response
    {
        $user = $this->getUser();
        if ($user && $user->getTags()){
            $posts = $postRepository->findPostsByTags($user->getTags()->toArray());
        } else {
            $posts = $postRepository->findAll();
        }
        return $this->render('post/index.html.twig', [
            'posts' => $posts,
        ]);
    }

    #[Route('/new', name: 'app_post_new', methods: ['GET', 'POST'])]
    #[IsGranted('IS_AUTHENTICATED_FULLY')]
    public function new(Request $request, PostRepository $postRepository, CategoryRepository $categoryRepository, TagRepository $tagRepository): Response
    {
        if ($request->isMethod('POST')) {
            $content = $request->request->get('content');
            $parameters = $request->request->all();
            $tagIds = $parameters['tags'];
            $post = new Post();
            $post->setContent($content);
            $post->setAuthor($this->getUser());
            $tags = $tagRepository->findBy(['id' => $tagIds]);
            foreach ($tags as $tag) {
                $post->addTag($tag);
            }
            $postRepository->save($post, true);
            return $this->redirectToRoute('app_post_show', ['id' => $post->getAuthor()->getId()], Response::HTTP_SEE_OTHER);
        }
        return $this->renderForm('post/new.html.twig', [
            'categories' => $categoryRepository->findAll(),
        ]);
    }

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

    #[Route('/{id}', name: 'app_post_show', methods: ['GET'])]
    public function showUserPosts(PostRepository $postRepository, User $user): Response
    {
        return $this->render('post/user_posts.html.twig', [
            'posts' => $postRepository->findAllByAuthor(
                $user
            )
        ]);
    }

    #[Route('/{id}/edit', name: 'app_post_edit', methods: ['GET', 'POST'])]
    #[IsGranted('IS_AUTHENTICATED_FULLY')]
    public function edit(Request $request, Post $post, PostRepository $postRepository, CategoryRepository $categoryRepository, TagRepository $tagRepository): Response
    {
        if ($request->isMethod('POST')) {
            $content = $request->request->get('content');
            $parameters = $request->request->all();
            $tagIds = $parameters['tags'];
            $post->setContent($content);
            $tags = $tagRepository->findBy(['id' => $tagIds]);
            $postTags = $post->getTags();
            foreach ($postTags as $postTag) {
                if (!in_array($postTag->getId(), $tagIds)) {
                    $post->removeTag($postTag);
                }
            }
            foreach ($tags as $tag) {
                $post->addTag($tag);
            }
            $postRepository->save($post, true);
            return $this->redirectToRoute('app_post_show', ['id' => $post->getAuthor()->getId()], Response::HTTP_SEE_OTHER);
        }
        return $this->renderForm('post/edit.html.twig', [
            'post'=> $post
        ]);
    }

    #[Route('/{id}', name: 'app_post_delete', methods: ['POST'])]
    #[IsGranted('IS_AUTHENTICATED_FULLY')]
    public function delete(Request $request, Post $post, PostRepository $postRepository): Response
    {
        if ($this->isCsrfTokenValid('delete' . $post->getId(), $request->request->get('_token'))) {
            $postRepository->remove($post, true);
        }

        return $this->redirectToRoute('app_post_show', ['id' => $post->getAuthor()->getId()], Response::HTTP_SEE_OTHER);
    }
}
