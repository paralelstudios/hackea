//
//  Cause.swift
//  Causa
//
//  Created by Pixnabi on 4/1/17.
//  Copyright © 2017 Pixnabilab. All rights reserved.
//

import Foundation
import Alamofire

class Cause: NSObject {
    
    static var baseUrl = "http://ec2-34-207-173-114.compute-1.amazonaws.com/" //"http://192.168.99.100/"
    
    class func registerUserWith(name: String, phone: String, email: String, password: String, completionHandler: @escaping (_ success: Bool, _ data: [String:Any]?, _ error: String?) -> ()) {
        
        let url = "\(self.baseUrl)api/users"
        
        let params = ["email":email,
                      "phone":phone,
                      "name":name,
                      "password":password]
        
        request(url, method: .post, parameters: params, encoding: URLEncoding.default, headers: nil).responseJSON { (response) in
            if let data = response.result.value as? [String:Any] {
                if let success = data["success"] as? Bool {
                    completionHandler(success, data, nil)
                } else {
                    completionHandler(false, nil, "Error con el registro")
                }
            } else {
                completionHandler(false, nil, "Error con el registro")
            }
        }
    }
    
    class func registerOrganization(name: String, userId: String,  completionHandler: @escaping (_ success: Bool, _ data: [String:Any]?, _ error: String?) -> ()) {
        let url = "\(self.baseUrl)api/orgs"
        
        let params = ["name":name,
                      "user_id":userId]
        
        request(url, method: .post, parameters: params, encoding: URLEncoding.default, headers: nil).responseJSON { (response) in
            if let data = response.result.value as? [String:Any] {
                if let success = data["success"] as? Bool {
                    completionHandler(success, data, nil)
                } else {
                    completionHandler(false, nil, "Error con el registro")
                }
            } else {
                completionHandler(false, nil, "Error con el registro")
            }
        }
    }
    
    class func getOrganizations(name: String!,  completionHandler: @escaping (_ success: Bool, _ data: [String:Any]?, _ error: String?) -> ()) {
        let url = "\(self.baseUrl)api/orgs"
        
        request(url, method: .get, parameters: name != nil ? ["name":name] : nil, encoding: URLEncoding.default, headers: nil).responseJSON { (response) in
            if let error = response.error {
                completionHandler(false, nil, error.localizedDescription)
                return
            }
//            print("Value: \(response.result.value)")
            if let data = response.result.value as? [String:Any] {
                completionHandler(true, data, nil)
            } else {
                completionHandler(false, nil, "Error con el get de organizaciones")
            }
        }
    }
    
    
    class func ping(completionHandler: @escaping (_ success: Bool, _ data: [String:Any]?, _ error: String?) -> ()) {
        
        let url = "\(self.baseUrl)_ping"
        
        request(url, method: .get, parameters: nil, encoding: JSONEncoding.default, headers: nil).responseJSON { (response) in
            print("Error: \(response.result.error)")
            print("Value: \(response.result.value)")
        }
    }
}

