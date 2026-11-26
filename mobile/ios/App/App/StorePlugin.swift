import Foundation
import Capacitor
import StoreKit

// Keymood Pro in the App Store build: one non-consumable in-app purchase, through StoreKit 2
// directly (Dafa, 26 Nov: our own small module, no RevenueCat - no third-party service, no
// account, nothing collected). Apple is the merchant and checks the receipt: a transaction
// reaches us already verified, or we ignore it. The page (index.html, NATIVE) calls this as
// Capacitor.registerPlugin('Store').
//
//   products({ids})  -> {products: [{id, displayName, displayPrice}]}   price as the store
//                       shows it in the buyer's country and currency (HIG: show the total)
//   purchase({id})   -> {status: purchased | cancelled | pending | unverified}
//   owned()          -> {ids}   what this Apple account owns, from the device's entitlements
//   restore()        -> {ids}   asks the App Store to sync first (guideline 3.1.1 needs a
//                       visible restore for a non-consumable), then the same as owned()
//   event "owned"    -> {ids}   after a purchase made elsewhere, a refund or an Ask to Buy
//                       approval arrives while the app runs
@objc(StorePlugin)
public class StorePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "StorePlugin"
    public let jsName = "Store"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "products", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "purchase", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "owned", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "restore", returnType: CAPPluginReturnPromise)
    ]
    private var updates: Task<Void, Never>?

    override public func load() {
        // Apple's rule: listen for transactions from the moment the app starts, or a purchase
        // finished while the app was closed (or approved later by a parent) is never finished.
        updates = Task.detached { [weak self] in
            for await result in Transaction.updates {
                if case .verified(let t) = result { await t.finish() }
                await self?.emitOwned()
            }
        }
    }

    deinit { updates?.cancel() }

    @objc func products(_ call: CAPPluginCall) {
        let ids = call.getArray("ids", String.self) ?? []
        Task {
            do {
                let list = try await Product.products(for: ids)
                call.resolve(["products": list.map { ["id": $0.id, "displayName": $0.displayName, "displayPrice": $0.displayPrice] }])
            } catch {
                call.reject(error.localizedDescription)
            }
        }
    }

    @objc func purchase(_ call: CAPPluginCall) {
        guard let id = call.getString("id") else { call.reject("No product id"); return }
        Task {
            do {
                guard let product = try await Product.products(for: [id]).first else {
                    call.reject("Product not found"); return
                }
                switch try await product.purchase() {
                case .success(let verification):
                    if case .verified(let t) = verification {
                        await t.finish()
                        call.resolve(["status": "purchased"])
                    } else {
                        call.resolve(["status": "unverified"])
                    }
                case .userCancelled:
                    call.resolve(["status": "cancelled"])
                case .pending:
                    call.resolve(["status": "pending"])      // Ask to Buy, or a payment to confirm
                @unknown default:
                    call.resolve(["status": "cancelled"])
                }
            } catch {
                call.reject(error.localizedDescription)
            }
        }
    }

    @objc func owned(_ call: CAPPluginCall) {
        Task { call.resolve(["ids": await ownedIds()]) }
    }

    @objc func restore(_ call: CAPPluginCall) {
        Task {
            // sync() asks for the Apple ID password; a cancel there still leaves the local
            // entitlements to read, so it is not an error to the page.
            try? await AppStore.sync()
            call.resolve(["ids": await ownedIds()])
        }
    }

    private func ownedIds() async -> [String] {
        var ids: [String] = []
        for await result in Transaction.currentEntitlements {
            if case .verified(let t) = result, t.revocationDate == nil { ids.append(t.productID) }
        }
        return ids
    }

    private func emitOwned() async {
        let ids = await ownedIds()
        notifyListeners("owned", data: ["ids": ids])
    }
}

// Capacitor finds npm plugins by itself; a plugin that lives in the app target is registered
// here. Main.storyboard names this class instead of CAPBridgeViewController.
class MainViewController: CAPBridgeViewController {
    override open func capacitorDidLoad() {
        bridge?.registerPluginInstance(StorePlugin())
    }
}
