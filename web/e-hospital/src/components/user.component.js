import React, { Component } from "react";

import { authenticationService } from '../_services';

export default class User extends Component {

    constructor(props) {
        super(props);
        //this.state = {isToggleOn: true};

        // redirect to home if already logged in
        // if (authenticationService.currentUserValue) { 
        //     this.props.history.push('/');
        // }
    }

    login(e) {
        e.preventDefault();
        let username = document.getElementById('username').value
        let password = document.getElementById('password').value
        // console.log(username)
        // console.log(password)
        // const requestOptions = {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({ username, password })
        // };
        authenticationService.login(username, password)
        .then(
            user => {
                //const { from } = this.props.location.state || { from: { pathname: "/" } };
                //this.props.history.push(from);
                console.log("ok")
            },
            error => {
                // setSubmitting(false);
                // setStatus(error);
                console.log('error')
            }
        );
        // return fetch('http://35.223.248.94/api/login/', requestOptions)
    }

    render() {
        return (
            <form>
                <h3>Truy xuất hồ sơ thông tin của bạn</h3>

                <div className="form-group">
                    <label>Tài khoản</label>
                    <input id="username" type="text" className="form-control" placeholder="Nhập tài khoản" />
                </div>

                <div className="form-group">
                    <label>Mật khẩu </label>
                    <input id="password" type="password" className="form-control" placeholder="Nhập mật khẩu" />
                </div>

                <button onClick={this.login}> Đăng nhâp </button>
            </form>
        );
    }
}