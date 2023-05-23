<?php

namespace App\Form;

use App\Entity\Material;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Symfony\Component\Form\Extension\Core\Type\FileType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Validator\Constraints\File;

class MaterialType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('name', TextType::class)
            ->add('fileLink', FileType::class, [
                'mapped' => false,
                'constraints' => [
                    new File([
                        'maxSize' => '10M',
                        'mimeTypes' => [
                            'application/pdf',
                            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                            'image/jpeg',
                            'image/jpg',
                        ],
                        'mimeTypesMessage' => 'Пожалуйста, загрузите файл валидного формата'
                    ])
                ]
            ])
            ->add('mimeType', ChoiceType::class, [
                'choices' => [
                    'PDF' => 'application/pdf',
                    'DOCX' => 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'DOC' => 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'PPTX' => 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'PPT' => 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'JPEG' => 'image/jpeg',
                ]
            ])
            ->add('isPrivate');
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => Material::class,
        ]);
    }
}
