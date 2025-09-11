using System;

namespace BeastMode.RmDdd.Examples.ECommerce
{
    /// <summary>
    /// Order line entity representing a line item in an order.
    /// This is an entity within the Order aggregate following .NET conventions.
    /// </summary>
    public class OrderLine
    {
        public ProductId ProductId { get; }
        public int Quantity { get; private set; }
        public decimal UnitPrice { get; private set; }
        
        public OrderLine(ProductId productId, int quantity, decimal unitPrice)
        {
            ProductId = productId ?? throw new ArgumentNullException(nameof(productId));
            
            if (quantity <= 0)
            {
                throw new ArgumentException("Quantity must be positive", nameof(quantity));
            }
            
            if (unitPrice < 0)
            {
                throw new ArgumentException("Unit price cannot be negative", nameof(unitPrice));
            }
            
            Quantity = quantity;
            UnitPrice = unitPrice;
        }
        
        public void UpdateQuantity(int quantity)
        {
            if (quantity <= 0)
            {
                throw new ArgumentException("Quantity must be positive", nameof(quantity));
            }
            
            Quantity = quantity;
        }
        
        public void UpdateUnitPrice(decimal unitPrice)
        {
            if (unitPrice < 0)
            {
                throw new ArgumentException("Unit price cannot be negative", nameof(unitPrice));
            }
            
            UnitPrice = unitPrice;
        }
        
        public decimal LineTotal => UnitPrice * Quantity;
        
        public override bool Equals(object? obj)
        {
            if (obj is not OrderLine other) return false;
            if (ReferenceEquals(this, other)) return true;
            
            return ProductId.Equals(other.ProductId);
        }
        
        public override int GetHashCode()
        {
            return ProductId.GetHashCode();
        }
        
        public override string ToString()
        {
            return $"OrderLine {{ ProductId = {ProductId}, Quantity = {Quantity}, UnitPrice = {UnitPrice:C}, LineTotal = {LineTotal:C} }}";
        }
    }
}