// kfGo site settings. Edit these values; no other file needs to change.
window.KFGO = {
  // WhatsApp numbers (country code, no +). Orders go to "orders".
  whatsapp: { orders: "919633444723", backup: "919633444790" },
  phoneDisplay: ["+91 96334 44723", "+91 96334 44790"],
  email: "office@kfgo.in",

  // UPI: fill in the company UPI ID (e.g. "kfgo@sbi") to show UPI pay at checkout.
  upi: { id: "", payee: "KF Travel and Logistics Pvt Ltd" },

  // Razorpay: once the account is live, paste the Key ID (rzp_live_...) to enable card/netbanking checkout.
  razorpayKey: "",

  // Optional: Google Apps Script web-app URL that writes each order into KF Ledger as a Lead.
  leadEndpoint: ""
};
