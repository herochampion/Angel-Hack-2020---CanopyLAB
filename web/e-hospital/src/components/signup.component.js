import React, { Component } from "react";

export default class SignUp extends Component {
    render() {
        return (
            <form>
                <h3>Tạo tài khoản bác sĩ</h3>

                <div className="form-group">
                    <label>Tên</label>
                    <input type="text" className="form-control" placeholder="First name" />
                </div>

                <div className="form-group">
                    <label>Họ và tên lót</label>
                    <input type="text" className="form-control" placeholder="Last name" />
                </div>

                <div className="form-group">
                    <label>Địa chỉ email</label>
                    <input type="email" className="form-control" placeholder="Enter email" />
                </div>

                <div className="form-group">
                    <label>Mật khẩu</label>
                    <input type="password" className="form-control" placeholder="Enter password" />
                </div>

                <button type="submit" className="btn btn-primary btn-block">Đăng kí</button>
                <p className="forgot-password text-right">
                    Đã có tài khoản <a href="#">Đăng nhập?</a>
                </p>
            </form>
        );
    }
}