<?php

namespace App\Form;

use App\Entity\User;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Symfony\Component\Form\Extension\Core\Type\IntegerType;
use Symfony\Component\Form\Extension\Core\Type\TelType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class UserType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('email')
            ->add('fullName', TextType::class)
            ->add('phoneNumber', TelType::class)
            ->add('age', IntegerType::class)
            ->add('almaMater', ChoiceType::class, [
                'choices' => [
                    'Cреднее общее образование' => 'Cреднее общее образование',
                    'Среднее профессиональное образование' => 'Среднее профессиональное образование',
                    'Бакалавриат' => 'Бакалавриат',
                    'Магистратура' => 'Магистратура'
                ],
            ])
            ->add('interests', TextType::class)
        ;
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => User::class,
        ]);
    }
}
