# sales/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem
from .forms import OrderItemForm
from django.contrib import messages

@login_required
def my_orders(request):
    orders = Order.objects.filter(cashier=request.user)
    return render(request, 'sales/order_list.html', {'orders': orders})

@login_required
def product_list(request):
    """បង្ហាញផលិតផល active ទាំងអស់ តម្រៀប A–Z"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'sales/product_list.html', {'products': products})

@login_required
def product_detail(request, pk):
    """បង្ហាញព័ត៌មានលម្អិតសម្រាប់ផលិតផលតែមួយ។ Return 404 ប្រសិនបើរកមិនឃើញ"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'sales/product_detail.html', {'product': product})

@login_required
def order_list(request):
    """បង្ហាញការបញ្ជាទិញទាំងអស់ ថ្មីបំផុតមុន"""
    orders = Order.objects.all()
    return render(request, 'sales/order_list.html', {'orders': orders})


@login_required
def create_order(request):
    """Instantly create an open order and jump straight to the add-items page."""
    order = Order.objects.create(
        cashier=request.user,
        status='open',
    )
    return redirect('add_item', pk=order.pk)


@login_required
def add_item(request, pk):
    order = get_object_or_404(Order, pk=pk)

    # 🚫 Prevent editing non-open orders
    if order.status != 'open':
        messages.error(
            request,
            f"Cannot modify this order because it is {order.status}."
        )
        return redirect('order_list')

    if request.method == 'POST':

        # ✅ Mark Paid
        if 'mark_paid' in request.POST:
            order.status = 'paid'
            order.save()

            messages.success(request, "Order marked as paid.")
            return redirect('order_list')

        # ❌ Cancel Order
        if 'cancel_order' in request.POST:
            order.status = 'cancelled'
            order.save()

            messages.warning(request, "Order has been cancelled.")
            return redirect('order_list')

        # ➕ Add Item
        item_form = OrderItemForm(request.POST)

        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.order = order
            item.unit_price = item.product.price
            item.save()

            # 🔥 Deduct stock
            product = item.product
            product.stock -= item.quantity
            product.save()

            messages.success(request, "Item added successfully.")

            return redirect('add_item', pk=order.pk)

    else:
        item_form = OrderItemForm()

    return render(request, 'sales/add_item.html', {
        'order': order,
        'item_form': item_form,
        'items': order.items.select_related('product'),
    })