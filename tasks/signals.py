from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from tasks.models import TodoItem, Category, Priority
from collections import Counter


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_added(sender, instance, action, model, **kwargs):
    if action != "post_add":
        return

    for cat in instance.category.all():
        slug = cat.slug

        new_count = 0
        for task in TodoItem.objects.all():
            new_count += task.category.filter(slug=slug).count()

        Category.objects.filter(slug=slug).update(todos_count=new_count)


@receiver(m2m_changed, sender=TodoItem.category.through)
def task_cats_removed(sender, instance, action, model, **kwargs):
    if action != "post_remove":
        return

    for c in Category.objects.all():
        Category.objects.filter(slug=c.slug).update(todos_count=0)

    cat_counter = Counter()
    for t in TodoItem.objects.all():
        for cat in t.category.all():
            cat_counter[cat.slug] += 1

    for slug, new_count in cat_counter.items():
        Category.objects.filter(slug=slug).update(todos_count=new_count)


@receiver(post_save, sender=TodoItem)
def task_prts_changed(sender, instance, model=TodoItem, **kwargs):
    for prt in Priority.objects.all():
        prt.todos_count = prt.tasks.count()
        prt.save()


@receiver(post_delete, sender=TodoItem)
def delete(sender, instance, using, *args, **kwargs):
    for c in Category.objects.all():
        Category.objects.filter(slug=c.slug).update(todos_count=0)

    cat_counter = Counter()
    for t in TodoItem.objects.all():
        for cat in t.category.all():
            cat_counter[cat.slug] += 1

    for slug, c_new_count in cat_counter.items():
        Category.objects.filter(slug=slug).update(todos_count=c_new_count)

    for prt in Priority.objects.all():
        prt.todos_count = prt.tasks.count()
        prt.save()
