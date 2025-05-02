from django.contrib import admin

from .models import Comment, Event


class CommentInline(admin.TabularInline):  # o admin.StackedInline si preferís otra vista
    model = Comment
    extra = 1
    readonly_fields = ("created_at",)
    fields = ("title", "text", "user", "created_at")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "scheduled_at", "organizer", "created_at")
    list_filter = ("scheduled_at", "organizer")
    search_fields = ("title", "description", "organizer__username")
    ordering = ("-scheduled_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {
            "fields": ("title", "description", "scheduled_at", "organizer")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    inlines = [CommentInline]  # Acá se incluyen los comentarios

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "event", "created_at")
    list_filter = ("event", "user")
    search_fields = ("title", "text", "user__username", "event__title")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

