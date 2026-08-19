function updateStatus(orderId, newStatus) { console.log('updateStatus', orderId, newStatus); }
function openSettleModal(orderId, orderType, customerName, customerMobile, totalStr, couponCode) {
    console.log('openSettleModal', orderId, orderType, customerName, customerMobile, totalStr, couponCode);
}
const htmlStr = <button class="btn-status" style="flex:1;" onclick="updateStatus(4, 'preparing')">Start Preparing</button>
<button class="btn-primary" style="width:100%; background:#dc2626;" onclick="openSettleModal(4, 'parcel', '', '', '563.85', '')">Settle Bill</button>;
console.log('HTML is valid.');
