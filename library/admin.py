from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Book, category, course, profile, AboutSection, Contactsettings
from .models import OrganizationSetting, SlideShow, SiteContentDetail, CourseOrder

admin.site.register(Book)
admin.site.register(category)
admin.site.register(profile)
admin.site.register(course)
admin.site.register(AboutSection)
admin.site.register(Contactsettings)
admin.site.register(OrganizationSetting)
admin.site.register(SlideShow)
admin.site.register(SiteContentDetail)


@admin.register(CourseOrder)
class CourseOrderAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'colored_transaction_id', 'colored_status', 'tarehe_ya_oda')
    list_filter = ('status', 'course')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'course__title', 'transaction_id')
    list_per_page = 20
    ordering = ('-tarehe_ya_oda',)
    actions = ['approve_selected_orders', 'reject_selected_orders']

    # ── Admins should NEVER add orders (only students do via checkout) ──
    def has_add_permission(self, request):
        return False

    # ── When viewing/editing an order, lock all fields except status ──
    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ('student', 'course', 'transaction_id', 'tarehe_ya_oda')
        return ('tarehe_ya_oda',)

    fieldsets = (
        ('Maelezo ya Mwanafunzi', {
            'fields': ('student', 'course', 'tarehe_ya_oda'),
        }),
        ('Uhakiki wa Malipo', {
            'fields': ('transaction_id', 'status'),
            'description': mark_safe(
                '<div style="background:#fff3cd; border:1px solid #ffc107; padding:10px 14px; '
                'border-radius:8px; margin-bottom:8px; font-size:0.9em;">'
                '<strong>⚠️ HATUA YA UHAKIKI:</strong> '
                'Angalia <strong>Namba ya Muamala (Transaction ID)</strong> iliyo hapa. '
                'Linganisha na ujumbe wa M-Pesa/Tigo Pesa uliokuja kwenye simu yako. '
                'Kama zinaoanana — badilisha Hali kuwa <strong>Imekubaliwa</strong>. '
                'Kama hazioani — chagua <strong>Imekataliwa</strong>.'
                '</div>'
            ),
        }),
    )

    def colored_transaction_id(self, obj):
        return format_html(
            '<code style="background:#dbeafe; color:#1d4ed8; padding:3px 10px; '
            'border-radius:5px; font-weight:bold; font-size:0.9em; letter-spacing:0.05em;">{}</code>',
            obj.transaction_id
        )
    colored_transaction_id.short_description = 'Transaction ID (Linganisha na SMS)'

    def colored_status(self, obj):
        config = {
            'pending':  ('#92400e', '#fef3c7', '⏳ Inasubiri'),
            'Approved': ('#14532d', '#dcfce7', '✅ Imekubaliwa'),
            'Rejected': ('#7f1d1d', '#fee2e2', '❌ Imekataliwa'),
        }
        color, bg, label = config.get(obj.status, ('#333', '#eee', obj.status))
        return format_html(
            '<span style="background:{}; color:{}; padding:3px 12px; '
            'border-radius:20px; font-size:0.82em; font-weight:700;">{}</span>',
            bg, color, label
        )
    colored_status.short_description = 'Hali'

    @admin.action(description='✅ Idhinisha oda zilizochaguliwa')
    def approve_selected_orders(self, request, queryset):
        updated = queryset.update(status='Approved')
        self.message_user(request, f'✅ Oda {updated} zimeidhinishwa. Wanafunzi wataweza kuona kozi zao.')

    @admin.action(description='❌ Kataa oda zilizochaguliwa')
    def reject_selected_orders(self, request, queryset):
        updated = queryset.update(status='Rejected')
        self.message_user(request, f'❌ Oda {updated} zimekataliwa.')