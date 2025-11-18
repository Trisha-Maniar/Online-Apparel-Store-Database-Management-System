// Check database connection status
async function checkDbStatus() {
  try {
    const res = await fetch('/api/products');
    const statusEl = document.getElementById('dbStatus');
    if (res.ok) {
      statusEl.innerHTML = `
        <div class="db-status-text">
          <div class="db-status-label">Database Connection</div>
          <div class="db-status-value">Connected ✓ (MySQL: online_apparel_store_dbms)</div>
        </div>
      `;
    } else {
      statusEl.innerHTML = `
        <div class="db-status-text">
          <div class="db-status-label">Database Connection</div>
          <div class="db-status-value" style="color: var(--danger-color);">Connection Error</div>
        </div>
      `;
    }
  } catch (e) {
    const statusEl = document.getElementById('dbStatus');
    statusEl.innerHTML = `
      <div class="db-status-text">
        <div class="db-status-label">Database Connection</div>
        <div class="db-status-value" style="color: var(--danger-color);">Unable to connect</div>
      </div>
    `;
  }
}

async function loadHome(){
  try{
    const sec = document.getElementById('products');
    sec.innerHTML = '<div class="loading">Loading products from database<span class="spinner"></span></div>';
    
    // Check DB status
    await checkDbStatus();
    
    const res = await fetch('/api/products');
    if(!res.ok) throw new Error('Failed to load products');
    const data = await res.json();
    if(data.error) throw new Error(data.error);
    
    sec.innerHTML='';
    
    if(data.length === 0){
      sec.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📦</div>
          <h3>No products available</h3>
          <p>The product table is empty in the database.</p>
        </div>
      `;
      return;
    }
    
    // Show database operation info
    const dbInfo = document.createElement('div');
    dbInfo.className = 'db-operation';
    dbInfo.textContent = `✓ Fetched ${data.length} products from 'product' table`;
    sec.appendChild(dbInfo);
    
    data.forEach(p=>{
      const el = document.createElement('div');
      el.className='product';
      
      const discountBadge = p.Discount && p.Discount > 0 
        ? `<span class="discount">${p.Discount}% OFF</span>` 
        : '';
      
      const finalPrice = p.Discount && p.Discount > 0
        ? (parseFloat(p.Price) * (1 - parseFloat(p.Discount)/100)).toFixed(2)
        : parseFloat(p.Price).toFixed(2);
      
      el.innerHTML = `
        <h4>${p.Product_Name || 'Unnamed Product'}</h4>
        <div class="brand">${p.Brand || 'Generic Brand'}</div>
        ${p.Description ? `<p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0.5rem 0;">${p.Description.substring(0, 100)}${p.Description.length > 100 ? '...' : ''}</p>` : ''}
        <div class="price">₹${finalPrice}</div>
        ${discountBadge}
        <div class="actions">
          <a href="product.html?id=${p.Product_ID}" class="btn secondary">View Details</a>
          <button class="add" data-id="${p.Product_ID}">Add to Cart</button>
        </div>
        <div style="margin-top: 0.5rem; font-size: 0.75rem; color: var(--text-secondary);">
          Product ID: ${p.Product_ID}
        </div>
      `;
      sec.appendChild(el);
    });
    
    // Add event listeners for add to cart buttons
    Array.from(document.getElementsByClassName('add')).forEach(b=> {
      b.addEventListener('click', async (e)=>{
        const id = e.target.getAttribute('data-id');
        const btn = e.target;
        const originalText = btn.textContent;
        
        btn.disabled = true;
        btn.textContent = 'Adding...';
        
        try{
          const custId = await getCustomerId();
          
          // Show DB operation
          const dbOp = document.createElement('div');
          dbOp.className = 'db-operation';
          dbOp.textContent = `→ INSERT INTO cart (Customer_ID, Product_ID, Quantity) VALUES (${custId}, ${id}, 1)`;
          btn.parentElement.appendChild(dbOp);
          
          const res = await fetch('/api/cart/add',{
            method:'POST', 
            headers:{'Content-Type':'application/json'}, 
            body: JSON.stringify({product_id:id, quantity:1, guest_id: custId})
          });
          const r = await res.json();
          
          if(r.ok) {
            dbOp.textContent = `✓ Successfully added to cart table`;
            dbOp.style.borderLeftColor = 'var(--secondary-color)';
            btn.textContent = '✓ Added!';
            btn.classList.add('success');
            setTimeout(() => {
              btn.textContent = originalText;
              btn.disabled = false;
              btn.classList.remove('success');
              dbOp.remove();
            }, 2000);
          } else {
            alert(r.error || 'Failed to add to cart');
            btn.textContent = originalText;
            btn.disabled = false;
            dbOp.remove();
          }
        }catch(err){
          alert('Error adding to cart: ' + err.message);
          btn.textContent = originalText;
          btn.disabled = false;
          console.error(err);
        }
      });
    });
  }catch(e){
    const sec = document.getElementById('products');
    sec.innerHTML = `
      <div class="alert error">
        <strong>Error loading products:</strong> ${e.message}
        <br><small>Check database connection and 'product' table</small>
      </div>
    `;
    console.error(e);
  }
}
loadHome();
